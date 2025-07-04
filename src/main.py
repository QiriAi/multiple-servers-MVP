from openai import OpenAI
import os
from datetime import datetime
from dotenv import load_dotenv
from src.engine_router import validate_tags, rank_engines, TAGS
from src.engine_loader import SEARCH_ENGINES
from src.llm_prompt_analyser import decompose_prompt
import google.generativeai as genai
import json
from src.jina_scraper import jina
from engines.deviantart import search_deviantart
from engines.google_images import google_image_search
from concurrent.futures import ThreadPoolExecutor
import logging
import time

def parallel_scrape(scrape_func, links, engine, max_workers=10):
    def wrapper(link):
        return {
            "context": scrape_func(link),
            "citation": link,
            "engine": engine
        }
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(wrapper, links))
    
def safe_search(search_func, inputs):
    try:
        return search_func(inputs)
    except Exception as e:
        print(f" {search_func.__name__} failed for '{inputs}': {e}")
        return []

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class SearchBot:
    ENGINES_USE_SUBQUESTIONS = {"google", "wikipedia", "jina_search"}
    ENGINES_USE_ENTITIES = {"arxiv", "astrophysics_data_system", "goodreads", "hackernews","imdb", "reddit"}
    ENGINES_USE_ENTITIES_NO_SCRAPING = {"github", "huggingface", "openstreetmap", "steam"}
    IMAGE_ENGINES = {"deviantart", "google_images"}

    def __init__(self, model="gemini-2.0-flash"):
        self.client = OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model = model

    def _get_subquestions(self, query: str):
        logging.info("Decomposing the query")
        result_json = decompose_prompt(query)
        try:
            result = json.loads(result_json)
            sub_queries = []
            sub_entities = []
            entity_dic = {}
            for sq in result.get("sub_queries", []):
                sub_queries.append(sq.get("sub_query"))
                sub_entities.append(sq.get("entities", []))
                for ent in sq.get("entities",[]):
                    if ent in entity_dic:
                        entity_dic[ent] += 1
                    else:
                        entity_dic[ent] = 1
            tags = result.get("tags", [])
            complexity_score = result.get("complexity_analysis", {}).get("complexity_score")
            return {
                "sub_queries": sub_queries,
                "entity_dic": entity_dic,
                "tags": tags,
                "complexity_score": complexity_score
            }
        except Exception as e:
            print(f"Error parsing subquestions: {e}")
            return {
                "sub_queries": [],
                "entity_dic": {},
                "tags": [],
                "complexity_score": []
            }
        
    def _get_top_entity_names(self, entity_dic, top_n=2):
        # Sort entities by count, descending
        sorted_entities = sorted(entity_dic.items(), key=lambda x: x[1], reverse=True)
        # Filter out entities with count <= 1 and then take top_n
        top_entities = [(entity, count) for entity, count in sorted_entities if count > 1][:top_n]
        # Fallback: if nothing passed the filter, just take 1 without filtering
        if not top_entities:
            top_entities = sorted_entities[:1]
        # Extract just the entity names
        top_entity_names = [entity for entity, count in top_entities]
        return top_entity_names
    
    # def _get_num_results(self, complexity_score, sub_questions):
    #     """
    #     This is the total number of questions we should
    #     ask overall -> base is the minimum!
    #     """
    #     base = 3
    #     bonus = int(complexity_score // 10)  # add 1 result per 10 points
    #     num_subq = len(sub_questions)
    #     return base + bonus + num_subq  # scale with both factors

    def _find_engines(self, tags: list):
        logging.info("Finding the engines")
        # Get tags and ranked engines
        tags = validate_tags(tags, TAGS)
        selected_engines = rank_engines(tags=tags)

        # must always include our baseline engines
        selected_engines += ["google", "jina_search"] 
        return selected_engines
        
    def _gather_search_jobs(self, selected_engines, sub_questions, top_entity_names):
        jobs = []

        for engine in selected_engines:
            search_func = SEARCH_ENGINES.get(engine)
            if not search_func:
                continue

            # Decide input source
            if engine in self.ENGINES_USE_SUBQUESTIONS:
                inputs = sub_questions
            elif engine in self.ENGINES_USE_ENTITIES or engine in self.ENGINES_USE_ENTITIES_NO_SCRAPING:
                inputs = top_entity_names
            else:
                continue

            # Build job: (engine, search_func, inputs)
            jobs.append((engine, search_func, inputs))

        return jobs
    
    def _run_search_jobs(self, jobs):
        def run_job(job):
            engine, search_func, inputs = job
            # Engines that return direct context (no scraping)
            if engine in self.ENGINES_USE_ENTITIES_NO_SCRAPING:
                logging.info(f"Running searching on {engine} with inputs {inputs}")
                return [{
                    "context": safe_search(search_func,i),
                    "citation": "NO_LINK_SINCE_NO_SCRAPING",
                    "engine": engine
                } for i in inputs]
            
            # Jina Search (special case, no scraping, returns JSON list)
            if engine == "jina_search":
                logging.info(f"Running Jina Search on inputs {inputs}")
                all_results = []
                for i in inputs:
                    response = safe_search(search_func, i)
                    if response.status_code == 200:
                        data = response.json().get("data", [])
                        for result in data[:3]: #limit to 3 results
                            content = result.get("content", "")
                            if not content:
                                continue
                            all_results.append({
                                "context": content,
                                "citation": result.get("url", ""),
                                "engine": "Jina Search"
                            })
                return all_results

            logging.info(f"Running searching on {engine} with inputs {inputs}")
            # Step 1: Search one-by-one (simplified)
            search_results = [safe_search(search_func,i) for i in inputs]

            # Step 2: Choose how many links to use
            num_links = 2 if engine == "google" else 1
            links = []
            for result in search_results:
                links.extend(result[:num_links])

            logging.info(f"Scraping links in parallel with jina on {engine} with inputs {links}")
            # Step 3: Scrape links in parallel with jina
            return parallel_scrape(jina, links, engine=engine)

        # Run one job per engine, in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            all_results = executor.map(run_job, jobs)

        # Flatten list of lists
        return [item for result in all_results for item in result]

    def _get_images(self, top_entity_names, top_images=3):
        def get_images_for_entity(entity):
            results = []
            logging.info(f"Getting images for {entity} from deviantart")
            results += safe_search(search_deviantart, entity)[:top_images]
            logging.info(f"Getting images for {entity} from google images")
            results += safe_search(google_image_search, entity)[:top_images]
            return results

        # Run get_images_for_entity in parallel per entity
        with ThreadPoolExecutor(max_workers=5) as executor:
            all_results = executor.map(get_images_for_entity, top_entity_names)

        # Flatten the results
        return [img for res in all_results for img in res]

    def _check_tokens(self, data: list):
        logging.info("Checking tokens")
        # Load the JSON file
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.0-flash")

        total_tokens = 0

        for item in data:
            try:
                # Count tokens for context
                context_tokens = model.count_tokens(str(item["context"])).total_tokens
                # Count tokens for citation (the link)
                citation_tokens = model.count_tokens(item["citation"]).total_tokens
                # Add both to total
                total_tokens += context_tokens + citation_tokens
            except Exception as e:
                print(f"Token count error for item {e}")
                total_tokens = "Error Calculating"

        return total_tokens
    
    def main(self, query):
        latency = {}
        start_time = time.perf_counter()

        # 1. Decompose prompt
        t0 = time.perf_counter()
        result = self._get_subquestions(query)
        latency["decompose_prompt"] = time.perf_counter() - t0

        sub_questions = result["sub_queries"]
        entity_dic = result["entity_dic"]
        tags = result["tags"]

        # 2. Select engines
        t0 = time.perf_counter()
        engines = self._find_engines(tags)
        latency["select_engines"] = time.perf_counter() - t0

        # 3. Get entities
        t0 = time.perf_counter()
        top_entity_names = self._get_top_entity_names(entity_dic, top_n=2)
        latency["get_entities"] = time.perf_counter() - t0

        # 4. Run search + scrape
        t0 = time.perf_counter()
        jobs = self._gather_search_jobs(engines, sub_questions, top_entity_names)
        info = self._run_search_jobs(jobs)
        latency["search_and_scrape"] = time.perf_counter() - t0

        # 5. Get images
        t0 = time.perf_counter()
        image_urls = self._get_images(top_entity_names)
        latency["get_images"] = time.perf_counter() - t0

        # 6. Count tokens
        t0 = time.perf_counter()
        #tokens = self._check_tokens(info)
        tokens = "NOT IMPLEMENTED"
        latency["token_check"] = time.perf_counter() - t0

        # Total time
        latency["total"] = time.perf_counter() - start_time

        # Final result
        final_result = {
            "query": query,
            "info": info,
            "images": image_urls, 
            "tokens": tokens,
            "latency": latency
        }

        return final_result

        #For non server testing
        # Generate a timestamped filename
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # filename = f"output/context_and_citation_{timestamp}.json"

        # # Save the file
        # with open(filename, "w", encoding="utf-8") as f:
        #     json.dump(final_result, f, indent=2)
        # return engines, tags, entity_dic, sub_questions

# Test the bot
if __name__ == "__main__":
    bot = SearchBot()
    query = "Explain the process of photosynthesis in plants and how it relates to climate change, including the role of carbon dioxide."
    #query = "Tell me about langchain"
    #query = "What is a black hole?"
    #query = "Best romantic movies"
    #query = "What is the cutest cat for me to buy?"
    bot.main(query)

# FIGURE OUT LATER
# PROBLEM!!! Similar books to harry potter (how can we use goodreads?)
# fo those that are not jina maybe i need to add something in the context like
# below are github links
# NEED TO MIX ENTITIES FOR SOME BECAUSE E.G. "cute" is an entity of 
# question: "find me a cute cat breed to buy" --> maybe i remove adjectives