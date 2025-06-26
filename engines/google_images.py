import requests
import json

def google_image_search(query, pageno=1):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    url = (
        f"https://www.google.com/search?q={query.replace(' ', '+')}"
        f"&tbm=isch&asearch=isch&async=_fmt:json,p:1,ijn:{pageno - 1}"
    )

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return []

    # Strip Google anti-JSON hijacking prefix
    clean_text = resp.text.lstrip(")]}'\n")

    try:
        data = json.loads(clean_text)
        images = data["ischj"]["metadata"]
    except Exception as e:
        print("Failed to parse:", e)
        return []

    results = []
    for item in images:
        try:
            result = {
                #"title": item["result"]["page_title"],
                "page_url": item["result"]["referrer_url"],
                "image_url": item["original_image"]["url"],
                "engine": "google_images"
                #"thumbnail_url": item["thumbnail"]["url"],
                #"source": item["result"].get("site_title", "Unknown"),
                #"snippet": item.get("text_in_grid", {}).get("snippet", "")
            }
            results.append(result)
        except Exception:
            continue

    return results


if __name__ == "__main__":
    query = "cute capybara"
    results = google_image_search(query)
    print(results)
    # for r in results[:3]:
    #     print(f"🖼️ {r['title']}\n🔗 {r['page_url']}\n📷 {r['image_url']}\n")
