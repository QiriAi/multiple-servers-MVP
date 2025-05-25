# SPDX-License-Identifier: AGPL-3.0-or-later
"""Baidu Web Search Scraper for chatbot integration"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import re

def search_baidu(query, page=1):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/113.0.0.0 Safari/537.36"
        )
    }
    offset = (page - 1) * 10
    params = {
        "wd": query,
        "pn": offset
    }
    url = f"https://www.baidu.com/s?{urlencode(params)}"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print("❌ Baidu request failed:", e)
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    results = []
    for result in soup.select("div.result"):
        title_tag = result.select_one("h3.t a")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = title_tag.get("href")

        # Try to extract snippet
        snippet = result.select_one("div.c-abstract, div.c-span18 p")
        snippet_text = snippet.get_text(strip=True) if snippet else ""

        results.append({
            "title": title,
            "url": link,
            "snippet": snippet_text
        })

    return results

if __name__ == "__main__":
    query = "人工智能"
    results = search_baidu(query)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}\n   {r['url']}\n   {r['snippet']}\n")
