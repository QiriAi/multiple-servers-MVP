import requests
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_SEARCH_CX")

ENDPOINT = "https://www.googleapis.com/customsearch/v1"

def search_google(query, count=5):
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        raise ValueError("Missing GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_CX in environment variables.")

    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": count,
    }

    resp = requests.get(ENDPOINT, params=params)
    if resp.status_code != 200:
        print("❌ Failed:", resp.status_code, resp.text)
        return []

    json = resp.json()
    items = json.get("items", [])

    results = []
    for item in items:
        results.append({
            "title": item.get("title"),
            "url": item.get("link"),
            "snippet": item.get("snippet", ""),
            "source": "Google"
        })

    return results

def get_google_urls(query, count=5):
    """Get just the URLs from Google search results."""
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        raise ValueError("Missing GOOGLE_SEARCH_API_KEY or GOOGLE_SEARCH_CX in environment variables.")

    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": count,
    }

    resp = requests.get(ENDPOINT, params=params)
    if resp.status_code != 200:
        print("❌ Failed:", resp.status_code, resp.text)
        return []

    json = resp.json()
    items = json.get("items", [])

    urls = [item["link"] for item in items]
    return urls


# 🔍 Example usage
if __name__ == "__main__":
    #res = search_google("how to learn python")
    #for r in res:
    #    print(f"{r['title']}\n{r['url']}\n{r['snippet']}\n")

    urls = get_google_urls("how to learn python")
    #print("Found URLs:")
    print(urls)
