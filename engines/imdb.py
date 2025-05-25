# TRY OMDB API if this breaks

import json
import requests

IMDB_SUGGESTION_URL = "https://v2.sg.media-imdb.com/suggestion/{letter}/{query}.json"
IMDB_HREF_BASE = "https://imdb.com/{category}/{entry_id}"
SEARCH_CATEGORIES = {"nm": "name", "tt": "title", "kw": "keyword", "co": "company", "ep": "episode"}


def search_imdb(query):
    query_key = query.replace(" ", "_").lower()
    url = IMDB_SUGGESTION_URL.format(letter=query_key[0], query=query_key)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return []

    suggestions = json.loads(response.text)
    results = []

    for entry in suggestions.get('d', []):
        entry_id = entry.get('id')
        category = SEARCH_CATEGORIES.get(entry_id[:2])
        if not category:
            continue

        title = entry.get('l', '')
        if 'q' in entry:
            title += f" ({entry['q']})"

        content = ''
        if 'rank' in entry:
            content += f"Rank: {entry['rank']} | "
        if 'y' in entry:
            content += f"Year: {entry['y']} | "
        if 's' in entry:
            content += f"Stars: {entry['s']}"

        image_url = entry.get('i', {}).get('imageUrl')
        if image_url:
            image_url_name, image_url_ext = image_url.rsplit('.', 1)
            if not image_url_name.endswith('_V1_'):
                magic = '_V1_QL75_UX280_CR0,0,280,414_'
            else:
                magic = 'QL75_UX280_CR0,0,280,414_'
            image_url = image_url_name + magic + '.' + image_url_ext

        results.append({
            "title": title,
            "url": IMDB_HREF_BASE.format(category=category, entry_id=entry_id),
            "content": content.strip(" |"),
            "thumbnail": image_url
        })

    return results


if __name__ == "__main__":
    query = "oppenheimer"
    results = search_imdb(query)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}\n   {r['url']}\n   {r['content']}")
        if r.get("thumbnail"):
            print(f"   Thumbnail: {r['thumbnail']}")
        print()
