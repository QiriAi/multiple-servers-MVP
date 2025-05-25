from bs4 import BeautifulSoup
import requests
from urllib.parse import urlencode

def search_yahoo_news(query, page=1):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/113.0.0.0 Safari/537.36"
        )
    }

    offset = (page - 1) * 10 + 1
    url = f"https://news.search.yahoo.com/search?{urlencode({'p': query})}&b={offset}"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print("❌ Error:", e)
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    articles = soup.select("ol.searchCenterMiddle > li div.compTitle")

    results = []
    for article in articles:
        title_tag = article.select_one("h4 > a")
        if not title_tag:
            continue

        title = title_tag.text.strip()
        link = title_tag["href"]
        if "yahoo.com" not in link:
            continue

        summary = article.find_next("p")
        snippet = summary.text.strip() if summary else ""

        results.append({
            "title": title,
            "url": link,
            "snippet": snippet
        })

    return results

if __name__ == "__main__":
    query = "AI research"
    results = search_yahoo_news(query)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}\n   {r['url']}\n   {r['snippet']}\n")

