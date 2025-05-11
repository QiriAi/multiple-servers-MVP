# engines/bing.py

import requests
import base64
from urllib.parse import urlparse, parse_qs, urlencode
from lxml import html
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("BING_API_KEY")
ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"

HEADERS = {
    "Ocp-Apim-Subscription-Key": API_KEY
}

def search_bing(query, count=5):
    if not API_KEY:
        raise ValueError("Missing BING_API_KEY in environment variables.")

    params = {
        "q": query,
        "count": count,
        "textDecorations": True,
        "textFormat": "HTML",
        "safeSearch": "Moderate",
    }

    resp = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if resp.status_code != 200:
        print("❌ Failed:", resp.status_code, resp.text)
        return []

    json = resp.json()
    web_results = json.get("webPages", {}).get("value", [])

    results = []
    for item in web_results:
        results.append({
            "title": item["name"],
            "url": item["url"],
            "snippet": item["snippet"],
            "source": "Bing"
        })

    return results

# 🔍 Example usage
if __name__ == "__main__":
    res = search_bing("how to learn python")
    for r in res:
        print(f"{r['title']}\n{r['url']}\n{r['snippet']}\n")
