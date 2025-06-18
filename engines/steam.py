"""Steam (store) chatbot integration script."""

import requests
from urllib.parse import urlencode


def search_steam_store(query, cc="us", lang="en"):
    base_url = "https://store.steampowered.com"
    query_params = {"term": query, "cc": cc, "l": lang}
    url = f"{base_url}/api/storesearch/?{urlencode(query_params)}"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return []

    results = []
    for item in data.get("items", []):
        app_id = item.get("id")
        title = item.get("name")
        url = f"{base_url}/app/{app_id}"
        thumbnail = item.get("tiny_image", "")

        price_data = item.get("price", {})
        currency = price_data.get("currency", "USD")
        final_price = price_data.get("final", 0) / 100
        price_str = f"{final_price:.2f} {currency}" if final_price else "Free"

        platforms = ', '.join(
            [platform for platform, supported in item.get("platforms", {}).items() if supported]
        ) or "Unknown"

        results.append({
            "title": title,
            "url": url,
            "price": price_str,
            "platforms": platforms,
            "thumbnail": thumbnail,
        })

    return results


if __name__ == "__main__":
    #query = "tell me about stardew valley"
    query = "stardew valley"
    results = search_steam_store(query)
    print(results)
    #for i, r in enumerate(results, 1):
    #    print(f"{i}. {r['title']}\n   {r['url']}\n   Price: {r['price']} | Platforms: {r['platforms']}\n")

# "farming games" doesn't work --> need specific game titles

    # entity search only
    # returns price, title, url, platforms
    # just ingest as is don't use jina ai