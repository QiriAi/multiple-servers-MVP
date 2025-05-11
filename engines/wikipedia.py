# engines/wikipedia.py

import requests
from urllib.parse import quote

WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
BASE_URL = "https://en.wikipedia.org/wiki/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; wikibot/1.0)"
}

def search_wikipedia(query):
    title = quote(query.strip().title())  # Wikipedia titles are capitalized
    url = WIKI_API + title

    try:
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code == 404:
            print("❌ No Wikipedia article found.")
            return []

        data = resp.json()
    except Exception as e:
        print("❌ Wikipedia API error:", e)
        return []

    if data.get("type") not in ["standard", "article"]:
        return []

    return [{
        "title": data.get("title", query),
        "url": data.get("content_urls", {}).get("desktop", {}).get("page", BASE_URL + title),
        "snippet": data.get("extract", "No summary available."),
        "source": "Wikipedia"
    }]

if __name__ == "__main__":
    results = search_wikipedia("Alan Turing")
    for r in results:
        print(f"{r['title']}\n{r['url']}\n{r['snippet']}\n")
