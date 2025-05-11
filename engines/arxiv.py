# engines/arxiv.py

import requests
from datetime import datetime
from lxml import etree

ARXIV_URL = (
    "https://export.arxiv.org/api/query"
    "?search_query=all:{query}&start={offset}&max_results={limit}"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; arxivbot/1.0; +https://arxiv.org)"
}

NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


def search_arxiv(query, page=1, limit=10):
    offset = (page - 1) * limit
    url = ARXIV_URL.format(query=query, offset=offset, limit=limit)

    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print("❌ arXiv request failed:", resp.status_code)
        return []

    try:
        dom = etree.fromstring(resp.content)
    except Exception as e:
        print("❌ XML parsing failed:", e)
        return []

    results = []

    for entry in dom.xpath('//atom:entry', namespaces=NAMESPACES):
        try:
            title = entry.xpath('.//atom:title', namespaces=NAMESPACES)[0].text.strip()
            summary = entry.xpath('.//atom:summary', namespaces=NAMESPACES)[0].text.strip()
            url = entry.xpath('.//atom:id', namespaces=NAMESPACES)[0].text.strip()

            # Optional fields
            authors = [
                a.text.strip() for a in entry.xpath('.//atom:author/atom:name', namespaces=NAMESPACES)
            ]
            published = entry.xpath('.//atom:published', namespaces=NAMESPACES)[0].text
            published_date = datetime.strptime(published, '%Y-%m-%dT%H:%M:%SZ')

            results.append({
                "title": title,
                "url": url,
                "snippet": summary,
                "source": "arXiv",
                "authors": authors,
                "published": published_date.strftime("%Y-%m-%d"),
            })
        except Exception:
            continue

    return results

if __name__ == "__main__":
    results = search_arxiv("reinforcement learning")
    for r in results:
        print(f"{r['title']} by {', '.join(r['authors'])}")
        print(r['url'])
        print(r['snippet'][:200], "...\n")
