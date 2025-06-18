# engines/wikipedia.py

import requests
from urllib.parse import quote

WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
BASE_URL = "https://en.wikipedia.org/wiki/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; wikibot/1.0)"
}

def search_wikipedia(query, limit=5):
    search_url = f"https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": limit,
    }

    try:
        resp = requests.get(search_url, params=params, headers=HEADERS)
        results = resp.json().get("query", {}).get("search", [])
    except Exception as e:
        print("❌ Wikipedia API error:", e)
        return []

    return [
        f"https://en.wikipedia.org/wiki/{quote(result['title'].replace(' ', '_'))}"
        for result in results
    ]

if __name__ == "__main__":
    results = search_wikipedia("what should i do if i have high blood sugar")
    print(results)
    
    # this works with full queries
    # gets web urls from the output
    # use jina ai to extract content afterwards
