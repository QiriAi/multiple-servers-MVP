## SORT BY DATE AND GET THE LATEST NEWS!!!!!!!

import requests
from datetime import datetime
from urllib.parse import urlencode
from dateutil.relativedelta import relativedelta

BASE_URL = "https://hn.algolia.com/api/v1"
RESULTS_PER_PAGE = 10

def search_hackernews(query: str, time_range: str = None, page: int = 1):
    search_type = "search"
    query_params = {}

    if not query:
        search_type = "search_by_date"
        query_params = {
            "tags": "front_page",
            "page": page - 1,
        }
    else:
        query_params = {
            "query": query,
            "page": page - 1,
            "hitsPerPage": RESULTS_PER_PAGE,
            "tagFilters": '["story"]',
        }

        if time_range:
            search_type = "search_by_date"
            timestamp = (datetime.now() - relativedelta(**{f"{time_range}s": 1})).timestamp()
            query_params["numericFilters"] = f"created_at_i>{timestamp}"

    full_url = f"{BASE_URL}/{search_type}?{urlencode(query_params)}"

    try:
        resp = requests.get(full_url)
        data = resp.json()
        results = []

        for hit in data.get("hits", []):
            object_id = hit.get("objectID")
            points = hit.get("points", 0)
            comments = hit.get("num_comments", 0)
            metadata = f"points: {points} | comments: {comments}" if points or comments else ""

            results.append({
                "title": hit.get("title") or f"author: {hit.get('author')}",
                "url": f"https://news.ycombinator.com/item?id={object_id}",
                "content": hit.get("url") or hit.get("comment_text") or hit.get("story_text") or "",
                "author": hit.get("author"),
                "metadata": metadata,
                "publishedDate": datetime.fromtimestamp(hit.get("created_at_i")),
            })

        return results

    except Exception as e:
        print(f"❌ Hacker News API failed: {e}")
        return []

if __name__ == "__main__":
    results = search_hackernews("OpenAI")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']} by {r['author']}")
        print(f"   {r['url']}")
        print(f"   {r['metadata']}")
        print(f"   {r['content'][:120]}...\n")
