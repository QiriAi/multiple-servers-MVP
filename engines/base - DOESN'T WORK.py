# engines/base.py

import requests
from urllib.parse import urlencode
from lxml import etree
from datetime import datetime

HEADERS = {
    "User-Agent": "searxng 1.0 (https://searxng.org)"
}

BASE_URL = (
    "https://api.base-search.net/cgi-bin/BaseHttpSearchInterface.fcgi"
    "?func=PerformSearch&{query}&boost=oa&hits={hits}&offset={offset}"
)

HITS = 10


def search_base(query, page=1):
    offset = (page - 1) * HITS
    query_args = {
        "query": urlencode({"query": query}),
        "hits": HITS,
        "offset": offset,
    }

    url = BASE_URL.format(**query_args)

    resp = requests.get(url, headers=HEADERS)
    print("✅ Status:", resp.status_code)
    print("📄 Response Preview:", resp.text[:1000])

    if resp.status_code != 200:
        print("BASE API failed:", resp.status_code)
        return []

    try:
        tree = etree.XML(resp.content)
    except Exception as e:
        print("XML parsing failed:", e)
        return []

    results = []
    for entry in tree.xpath('./result/doc'):
        title = url = content = "N/A"
        date_raw = None

        for field in entry:
            name = field.attrib.get("name", "")
            if name == "dctitle":
                title = field.text
            elif name == "dcdescription":
                content = (field.text or "")[:300] + "..." if field.text and len(field.text) > 300 else field.text
            elif name == "dclink":
                url = field.text
            elif name == "dcdate":
                date_raw = field.text

        # Try to parse the date
        published_date = None
        for fmt in ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d', '%Y-%m', '%Y']:
            try:
                published_date = datetime.strptime(date_raw, fmt)
                break
            except:
                pass

        results.append({
            "title": title or "Untitled",
            "url": url or "",
            "snippet": content or "No description available.",
            "source": "BASE"
        })

    return results

if __name__ == "__main__":
    results = search_base("climate change and agriculture")
    for r in results:
        print(f"{r['title']}\n{r['url']}\n{r['snippet']}\n")