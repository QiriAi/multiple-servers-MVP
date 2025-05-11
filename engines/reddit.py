# engines/reddit.py

import requests
from datetime import datetime
from urllib.parse import urlencode, urljoin

REDDIT_BASE_URL = "https://www.reddit.com/"
REDDIT_SEARCH_URL = REDDIT_BASE_URL + "search.json?{query}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; redditbot/1.0)"
}

def search_reddit(query, limit=10):
    encoded = urlencode({"q": query, "limit": limit})
    url = REDDIT_SEARCH_URL.format(query=encoded)

    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print("❌ Reddit search failed:", resp.status_code)
        return []

    data = resp.json()
    posts = data.get("data", {}).get("children", [])
    results = []

    for post in posts:
        post_data = post["data"]
        url = urljoin(REDDIT_BASE_URL, post_data["permalink"])
        title = post_data.get("title", "Untitled")
        text = post_data.get("selftext", "")
        if len(text) > 500:
            text = text[:500] + "..."
        created_utc = post_data.get("created_utc")
        published = datetime.utcfromtimestamp(created_utc).strftime('%Y-%m-%d') if created_utc else None

        results.append({
            "title": title,
            "url": url,
            "snippet": text if text else "[No text content]",
            "published": published,
            "source": "Reddit"
        })

    return results

if __name__ == "__main__":
    results = search_reddit("anxiety coping tips")
    for r in results:
        print(f"{r['title']} ({r['published']})\n{r['url']}\n{r['snippet']}\n")
