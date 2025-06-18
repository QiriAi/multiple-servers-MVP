"""
Doesn't connect to the papers only gives extracts 

"""
import requests
from datetime import datetime
from urllib.parse import urlencode
import os
from dotenv import load_dotenv

load_dotenv()

ADS_API_KEY = os.getenv("HARVARD_ADS_API_KEY")
ADS_BASE_URL = "https://api.adsabs.harvard.edu/v1/search/query"
ADS_UI_BASE_URL = "https://ui.adsabs.harvard.edu/abs/"

def search_ads(query, rows=5, page=1):
    headers = {
        "Authorization": f"Bearer {ADS_API_KEY}",
    }

    params = {
        "q": query,
        "fl": "bibcode,author,title,abstract,doi,date",
        "rows": rows,
        "start": rows * (page - 1),
    }

    url = f"{ADS_BASE_URL}?{urlencode(params)}"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("❌ Request failed:", e)
        return []

    docs = data.get("response", {}).get("docs", [])
    results = []

    for res in docs:
        title = res.get("title", [""])[0]
        url = ADS_UI_BASE_URL + res.get("bibcode", "") + "/"
        author = res.get("author", [])
        author = author[0] + " et al." if author else ""
        abstract = res.get("abstract", "")
        doi = res.get("doi", [])
        doi = doi[0] if isinstance(doi, list) and doi else None
        date = res.get("date", "")
        try:
            date = datetime.fromisoformat(date).strftime("%Y-%m-%d") if date else ""
        except ValueError:
            date = ""

        # results.append({
        #     "title": title,
        #     "url": url,
        #     "author": author,
        #     "abstract": abstract,
        #     "doi": doi,
        #     "publishedDate": date
        # })
        results.append(url)

    return results

if __name__ == "__main__":
    #query = "black hole accretion"
    query = "pluto"
    papers = search_ads(query)
    print(papers)
    # for i, paper in enumerate(papers, 1):
    #     print(f"{i}. {paper['title']}")
    #     print(f"   Author: {paper['author']}")
    #     print(f"   Date: {paper['publishedDate']}")
    #     print(f"   DOI: {paper['doi']}")
    #     print(f"   URL: {paper['url']}")
    #     print(f"   Abstract: {paper['abstract'][:300]}...\n")

# search in entities
# for now in mvp take urls and jina to scrape abstracts

# LATER AFTER MVP
# don't scrape returns multiple results and abstracts 
