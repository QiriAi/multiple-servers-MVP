from openai import OpenAI
import os
from dotenv import load_dotenv
from engines.bing import search_bing
from engines.goodreads import search_goodreads
from engines.arxiv import search_arxiv
from engines.reddit import search_reddit
from engines.wikipedia import search_wikipedia


load_dotenv()

class chatbot():
    valid_secondary_engines = {"books", "social", "scholarly", "encyclopedia"}
    
    def __init__(self, model="gemini-2.0-flash"):
        self.client = OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model = model

    def _classify_secondary_engine(self, query):
        """Use Gemini to choose the second engine."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an intent classifier that chooses the most appropriate information source for answering a user's query.\n"
                    "Select ONLY ONE of the following engine categories based on the nature of the query:\n\n"
                    "- `books`: for book titles, author names, reading suggestions, literary genres, or novel comparisons\n"
                    "- `social`: for subjective advice, lived experiences, real-world opinions, or community tips (e.g., Reddit-style)\n"
                    "- `scholarly`: for academic papers, scientific studies, peer-reviewed research, or formal datasets (e.g., arXiv)\n"
                    "- `encyclopedia`: for factual summaries or overviews about **people, places, events, history, culture, or definitions** (e.g., Wikipedia)\n"
                    "- `none`: if the query is generic or doesn’t clearly fit any of the above types\n\n"
                    "Only respond with one word: books, social, scholarly, encyclopedia, or none."
                )
            },
            {"role": "user", "content": f"Query: {query}\nCategory:"}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "text"},
                temperature=0
            )
            category = response.choices[0].message.content.strip().lower().replace(".", "")

            if category in self.valid_secondary_engines:
                return category
            return None  # If it's "none" or unrecognized
        except Exception as e:
            print("LLM classification failed:", e)
            return None
        
    def _get_search_results(self, query):
        results = []

        # Always include Bing
        try:
            bing_results = search_bing(query)
            print("\n🔹 Results from Bing:")
            for i, r in enumerate(bing_results):
                print(f"{i+1}. {r['title']}\n{r['url']}\n{r.get('snippet', '')}\n")
            results += bing_results
        except Exception as e:
            print("Bing failed:", e)

        # Optional second engine
        second = self._classify_secondary_engine(query)

        try:
            if second == "books":
                goodreads_results = search_goodreads(query)
                print("\n📚 Results from Goodreads:")
                for i, r in enumerate(goodreads_results):
                    print(f"{i+1}. {r['title']} by {r.get('author')}\n{r['url']}\n{r.get('snippet', '')}\n")
                results += goodreads_results
            
            elif second == "scholarly":
                arxiv_results = search_arxiv(query)
                print("\n📖 Results from arXiv:")
                for i, r in enumerate(arxiv_results):
                    authors = ', '.join(r.get('authors', []))
                    print(f"{i+1}. {r['title']} by {authors}\n{r['url']}\n{r.get('snippet', '')}\n")
                results += arxiv_results

            elif second == "social":
                reddit_results = search_reddit(query)
                print("\n👥 Results from Reddit:")
                for i, r in enumerate(reddit_results):
                    print(f"{i+1}. {r['title']} ({r['published']})\n{r['url']}\n{r['snippet']}\n")
                results += reddit_results

            elif second == "encyclopedia":
                wiki_results = search_wikipedia(query)
                print("\n📚 Results from Wikipedia:")
                for i, r in enumerate(wiki_results):
                    print(f"{i+1}. {r['title']}\n{r['url']}\n{r['snippet']}\n")
                results += wiki_results

            else:
                print("No second engine")

        except Exception as e:
            print(f"{second} engine failed:", e)

        return results


    def chat(self, query):
        """Main chatbot interface — fetches search results, injects into LLM, and returns a response."""
        search_results = self._get_search_results(query)

        # Format search results
        if not search_results:
            formatted_results = "No relevant search results found."
        else:
            formatted_results = "\n\n".join(
                f"{i+1}. {r['title']}\n{r['url']}\n{r.get('snippet', '')}" for i, r in enumerate(search_results[:5])
            )

            # Detect which engines were used (besides Bing)
            engine_context_notes = []
            if any(r.get("source") == "Reddit" for r in search_results):
                engine_context_notes.append(
                    "- Some insights come from Reddit, a user-generated platform. These may reflect personal experiences or opinions rather than verified facts. Interpret with caution and maintain a neutral perspective."
                )
            if any(r.get("source") == "arXiv" for r in search_results):
                engine_context_notes.append(
                    "- Some results are from arXiv, representing scientific research. They may be technical or preliminary."
                )
            if any(r.get("source") == "Wikipedia" for r in search_results):
                engine_context_notes.append(
                    "- Factual summaries may come from Wikipedia. These are generally reliable but not peer-reviewed."
                )
            if any(r.get("source") == "Goodreads" for r in search_results):
                engine_context_notes.append(
                    "- Book suggestions are from Goodreads and may reflect popular opinion or user reviews."

                )

            # Combine dynamic instructions
            engine_notes = "\n".join(engine_context_notes)
            system_prompt = (
                "You are a helpful assistant who uses web search results to answer the user's question clearly and usefully.\n"
                "Always cite or paraphrase relevant information, and use natural language.\n"
            )
            if engine_notes:
                system_prompt += "\nBefore answering, note:\n" + engine_notes

            # Construct message context
            messages = [
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": query},
                {"role": "system", "content": f"Here are search results:\n{formatted_results}"}
            ]

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "text"},
                temperature=0.7
            )
            print("\n:) Chatbot response:")
            return completion.choices[0].message.content.strip()
        except Exception as e:
            print("Chat generation failed:", e)
            return "Sorry, something went wrong while generating a response."


x = chatbot()
print(x.chat("boyfriend cheating tips"))