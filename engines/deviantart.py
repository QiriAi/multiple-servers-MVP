# engines/deviantart.py
import requests
import urllib.parse
from lxml import html

BASE_URL = 'https://www.deviantart.com'
SEARCH_URL = BASE_URL + '/search?{}'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; deviantartbot/1.0)"
}

results_xpath = '//div[@class="_2pZkk"]/div/div/a'
url_xpath = './@href'
title_xpath = './@aria-label'
thumbnail_xpath = './div/img/@src'


def extract_text(elements):
    if isinstance(elements, list) and elements:
        return elements[0].strip()
    return ""


def search_deviantart(query, page=1):
    url = SEARCH_URL.format(urllib.parse.urlencode({'q': query}))
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        if resp.status_code != 200:
            print("❌ DeviantArt request failed:", resp.status_code)
            return []
    except Exception as e:
        print("❌ DeviantArt error:", e)
        return []

    tree = html.fromstring(resp.text)
    results = []

    for node in tree.xpath(results_xpath):
        post_path = extract_text(node.xpath(url_xpath))
        #title = extract_text(node.xpath(title_xpath))
        thumbnail = extract_text(node.xpath(thumbnail_xpath))
        if thumbnail.startswith("data:"):
            continue  # ❌ Skip broken/placeholder images

        full_url = urllib.parse.urljoin(BASE_URL, post_path)
        #artist = post_path.split("/")[1] if len(post_path.split("/")) > 1 else "Unknown"

        results.append({
            #"title": title,
            #"artist": artist,
            "url": full_url,
            "thumbnail": thumbnail,
            "engine": "deviantart"
            # "text": (
            #     f"Title: {title}\n"
            #     f"Artist: {artist}\n"
            #     f"Image: {thumbnail}\n"
            #     f"Link: {full_url}\n"
            # )
        })

    return results


# ✅ CLI Test
if __name__ == "__main__":
    results = search_deviantart("anxiety")
    #for r in results[:5]:
    #    print(r["text"])
    print(results)

# best for entity matches
# returns url and thumbnail image
# no jina needed

