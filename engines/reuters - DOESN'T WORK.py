# engines/reuters.py

import requests
import json
from urllib.parse import quote_plus
from datetime import datetime, timedelta

REUTERS_API = "https://www.reuters.com/pf/api/v3/content/fetch/articles-by-search-v2"
BASE_URL = "https://www.reuters.com"
RESULTS_PER_PAGE = 20
SORT_ORDER = "relevance"

TIME_RANGE_MAP = {
    "day": 1,
    "week": 7,
    "month": 30,
    "year": 365,
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

def search_reuters(query, page=1, time_range=None):
    offset = (page - 1) * RESULTS_PER_PAGE

    # Step 1: Prepare query payload
    args = {
        "keyword": query,
        "offset": offset,
        "orderby": SORT_ORDER,
        "size": RESULTS_PER_PAGE,
        "website": "reuters"
    }

    if time_range in TIME_RANGE_MAP:
        start_date = datetime.now() - timedelta(days=TIME_RANGE_MAP[time_range])
        args["start_date"] = start_date.isoformat()

    query_string = quote_plus(json.dumps(args))
    url = f"{REUTERS_API}?query={query_string}"

    # Step 2: Create a session to get cookies
    session = requests.Session()

    # Step 3: Warm up the session with homepage request to get cookies
    try:
        session.get(BASE_URL, headers=HEADERS, timeout=5)
    except Exception as e:
        print("⚠️ Failed to warm up Reuters session:", e)

    # Step 4: Now call the search API with cookies and headers
    try:
        resp = session.get(url, headers=HEADERS)
        if resp.status_code != 200:
            print(f"❌ Reuters API failed: {resp.status_code}")
            return []

        articles = resp.json().get("result", {}).get("articles", [])
    except Exception as e:
        print("❌ Failed to fetch or parse Reuters data:", e)
        return []

    # Step 5: Parse and return results
    results = []
    for article in articles:
        try:
            results.append({
                "title": article.get("title", "Untitled"),
                "url": BASE_URL + article.get("canonical_url", ""),
                "snippet": article.get("description", "No description."),
                "published": datetime.strptime(
                    article.get("display_time"), "%Y-%m-%dT%H:%M:%SZ"
                ).strftime("%Y-%m-%d") if article.get("display_time") else None,
                "source": "Reuters"
            })
        except Exception:
            continue

    return results

if __name__ == "__main__":
    results = search_reuters("european elections", time_range="week")
    for r in results:
        print(f"{r['title']} ({r['published']})\n{r['url']}\n{r['snippet']}\n")
