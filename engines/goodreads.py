# engines/goodreads.py

from urllib.parse import urlencode, quote_plus
from lxml import html
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com/",
}

BASE_URL = "https://www.goodreads.com"

# XPaths for parsing
RESULTS_XPATH = "//table//tr"
THUMBNAIL_XPATH = ".//img[contains(@class, 'bookCover')]/@src"
URL_XPATH = ".//a[contains(@class, 'bookTitle')]/@href"
TITLE_XPATH = ".//a[contains(@class, 'bookTitle')]"
AUTHOR_XPATH = ".//a[contains(@class, 'authorName')]"
INFO_TEXT_XPATH = ".//span[contains(@class, 'uitext')]"

# --- REQUEST FUNCTION ---
def request_goodreads(query, page=1):
    args = {
        'q': query,
        'page': page
    }
    query_url = f"{BASE_URL}/search?{urlencode(args)}"
    return query_url

# --- RESPONSE PARSER FUNCTION ---
from lxml import html

def parse_goodreads(response_text):
    tree = html.fromstring(response_text)
    results = []

    rows = tree.xpath("//tr[@itemtype='http://schema.org/Book']")
    for row in rows:
        try:
            title_elem = row.xpath(".//a[contains(@class, 'bookTitle')]/span/text()")
            author_elem = row.xpath(".//a[contains(@class, 'authorName')]/span/text()")
            url_elem = row.xpath(".//a[contains(@class, 'bookTitle')]/@href")
            thumb_elem = row.xpath(".//img[contains(@class, 'bookCover')]/@src")
            info_elem = row.xpath(".//span[contains(@class, 'minirating')]/text()")

            # results.append({
            #     "title": title_elem[0].strip() if title_elem else None,
            #     "author": author_elem[0].strip() if author_elem else None,
            #     "url": "https://www.goodreads.com" + url_elem[0] if url_elem else None,
            #     "thumbnail": thumb_elem[0] if thumb_elem else None,
            #     "snippet": info_elem[0].strip() if info_elem else "",
            #     "source": "Goodreads"
            # })
            results.append("https://www.goodreads.com" + url_elem[0] if url_elem else None)
        except Exception:
            continue  # Skip malformed rows

    return results

# --- WRAPPER FUNCTION ---
def search_goodreads(query, page=1):
    url = request_goodreads(query, page)
    #print(f"🔍 Requesting: {url}")  # log URL

    resp = requests.get(url, headers=HEADERS)
    #print(f"✅ Status: {resp.status_code}")

    if resp.status_code != 200:
        print("❌ Request failed")
        return []

    # Check what the HTML looks like
   # print("🧾 HTML Preview:", resp.text[:500])

    results = parse_goodreads(resp.text)
    #print(f"📦 Parsed {len(results)} results")
    return results

if __name__ == "__main__":
    results = search_goodreads("books about dogs")
    print(results)

    # if not results:
    #     print("No results found.")

    # for r in results:
    #     print(f"{r['title']} by {r['author']}\n{r['url']}\n")

# search in entities
# receive url + jina