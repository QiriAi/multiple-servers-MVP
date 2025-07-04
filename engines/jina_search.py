import requests
from urllib.parse import quote_plus  # helps safely encode the search query
import os
from dotenv import load_dotenv
import json

load_dotenv()

api_key = os.getenv("JINA_API_KEY")

def jina_search(query: str):
    encoded_query = quote_plus(query)  # converts spaces to +, encodes special characters
    url = f"https://s.jina.ai/?q={encoded_query}"

    headers = {
        "Accept": "application/json",
        "Authorization": api_key, #has bearer prefix
        "X-Engine": "direct",
        "X-Retain-Images": "none"
    }

    response = requests.get(url, headers=headers)
    return response

if __name__ == "__main__":
    query = "hair"
    response = jina_search(query)
    if response.status_code == 200:
        results = response.json().get("data", [])
    
        info = []
        for result in results:
            if result.get("content", "") == "":
                continue
            else:
                item = {
                    "context": result.get("content", ""),
                    "citation": result.get("url", ""),
                    "engine": "Jina Search"
                }
                info.append(item)

        final_output = {"info": info}
        #print(final_output)
        with open("try", "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=2)