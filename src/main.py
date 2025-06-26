from openai import OpenAI
from datetime import datetime
import os
from dotenv import load_dotenv
from src.engine_router import validate_tags, rank_engines, TAGS
from src.engine_loader import SEARCH_ENGINES
from src.llm_prompt_analyser import decompose_prompt
import google.generativeai as genai
import json
from src.jina_scraper import jina
from engines.google import get_google_urls
from engines.deviantart import search_deviantart
from engines.google_images import google_image_search

load_dotenv()

class SearchBot:
    ENGINES_USE_SUBQUESTIONS = {"google", "wikipedia"}
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
        result_json = decompose_prompt(query)
        #print(result_json)
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
            #entities = result.get("entities", [])
            complexity_score = result.get("complexity_analysis", {}).get("complexity_score")
            return {
                "sub_queries": sub_queries,
                "entity_dic": entity_dic,
                #"sub_entities": sub_entities,
                "tags": tags,
                #"entities": entities,
                "complexity_score": complexity_score
            }
        except Exception as e:
            print(f"Error parsing subquestions: {e}")
            return {
                "sub_queries": [],
                "entity_dic": [],
                #"sub_entities": [],
                "tags": [],
                "complexity_score": []
            }
    
    def _get_num_results(self, complexity_score, sub_questions):
        """
        This is the total number of questions we should
        ask overall -> base is the minimum!
        """
        base = 3
        bonus = int(complexity_score // 10)  # add 1 result per 10 points
        num_subq = len(sub_questions)
        return base + bonus + num_subq  # scale with both factors

    def _find_engines(self, tags: list):
        # Get tags and ranked engines
        tags = validate_tags(tags, TAGS)
        selected_engines = rank_engines(tags=tags)
        return selected_engines
    
    def _base_line_queries(self, sub_questions: list):
        links = []
        info = []
        for sub_question in sub_questions:
            links.extend(get_google_urls(sub_question)[:2])
        for link in links:
            info.append({
                "context": jina(link),
                "citation": link,
                "engine": "google"
            })
        return info
    
    def _use_additional_engines(self, selected_engines, sub_questions, entity_dic, top_n=2):
        info = []
        # Sort entities by count, descending
        sorted_entities = sorted(entity_dic.items(), key=lambda x: x[1], reverse=True)

        # Filter out entities with count <= 1 and then take top_n
        top_entities = [(entity, count) for entity, count in sorted_entities if count > 1][:top_n]

        # Fallback: if nothing passed the filter, just take 1 without filtering
        if not top_entities:
            top_entities = sorted_entities[:1]

        # Extract just the entity names
        top_entity_names = [entity for entity, count in top_entities]

        for engine in selected_engines:
            search_func = SEARCH_ENGINES.get(engine)
            if not search_func:
                continue

            # Use sub-questions or entities depending on the engine
            if engine in self.ENGINES_USE_SUBQUESTIONS:
                for sub_question in sub_questions:
                    links = search_func(sub_question)
                    for link in links[:1]:  # or [:2] if you want more
                        info.append({
                            "context": jina(link),
                            "citation": link,
                            "engine": engine
                        })
            elif engine in self.ENGINES_USE_ENTITIES:
                for entity in top_entity_names:
                    links = search_func(entity)
                    for link in links[:1]:
                        info.append({
                            "context": jina(link),
                            "citation": link,
                            "engine": engine
                        })
            elif engine in self.ENGINES_USE_ENTITIES_NO_SCRAPING:
                for entity in top_entity_names:
                    info.append({
                            "context": search_func(entity),
                            "citation": "TEMPORARY MEASURE NO LINK",
                            "engine": engine
                        })                     
        return info
    
    def _get_images(self, entity_dic, top_n=2, top_images = 3):
        # Get top entities
        # Sort entities by count, descending
        sorted_entities = sorted(entity_dic.items(), key=lambda x: x[1], reverse=True)

        # Filter out entities with count <= 1 and then take top_n
        top_entities = [(entity, count) for entity, count in sorted_entities if count > 1][:top_n]

        # Fallback: if nothing passed the filter, just take 1 without filtering
        if not top_entities:
            top_entities = sorted_entities[:1]

        # Extract just the entity names
        top_entity_names = [entity for entity, count in top_entities]
        outputs = []

        for entity in top_entity_names:
            outputs += search_deviantart(entity)[:top_images] # append top 3 (default)
            outputs += google_image_search(entity)[:top_images] # append top 3 (default)
        return outputs

    def _check_tokens(self, data: list):
        # Load the JSON file
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.0-flash")

        total_tokens = 0

        for item in data:
            # Count tokens for context
            context_tokens = model.count_tokens(str(item["context"])).total_tokens
            # Count tokens for citation (the link)
            citation_tokens = model.count_tokens(item["citation"]).total_tokens
            # Add both to total
            total_tokens += context_tokens + citation_tokens

        return total_tokens

    def main(self, query):
        result = self._get_subquestions(query)
        sub_questions = result["sub_queries"]
        print(sub_questions)
        #complexity_score = result["complexity_score"]
        entity_dic = result["entity_dic"]
        print(entity_dic)
        tags = result["tags"]
        print(tags)
        #num_results = self._get_num_results(complexity_score, sub_questions)
        engines = self._find_engines(tags)
        print(engines)
        info1 = self._base_line_queries(sub_questions)
        info2 = self._use_additional_engines(engines, sub_questions, entity_dic)
        all_info = info1 + info2
        image_urls = self._get_images(entity_dic)

        final_result = {
            "query": query,
            "info": all_info,
            "images": image_urls, 
            "tokens": self._check_tokens(all_info)
        }

        return final_result
        # # Generate a timestamped filename
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # filename = f"output/context_and_citation_{timestamp}.json"

        # # Save the file
        # with open(filename, "w", encoding="utf-8") as f:
        #     json.dump(final_result, f, indent=2)
        #return num_results, engines, tags, entity_dic, sub_questions

# Test the bot
if __name__ == "__main__":
    bot = SearchBot()
    #query = "Explain the process of photosynthesis in plants and how it relates to climate change, including the role of carbon dioxide."
    #query = "Tell me about langchain"
    #query = "What is a black hole?"
    #query = "Best romantic movies"
    query = "What is the cutest cat for me to buy?"
    bot.main(query)

# FIGURE OUT LATER
# PROBLEM!!! Similar books to harry potter (how can we use goodreads?)
# fo those that are not jina maybe i need to add something in the context like
# below are github links
# NEED TO MIX ENTITIES FOR SOME BECAUSE E.G. "cute" is an entity of 
# question: "find me a cute cat breed to buy" --> maybe i remove adjectives