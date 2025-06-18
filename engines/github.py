import requests
from urllib.parse import urlencode
from dateutil import parser

def search_github_repos(query, max_results=5):
    base_url = 'https://api.github.com/search/repositories'
    query_url = f"{base_url}?{urlencode({'q': query, 'sort': 'stars', 'order': 'desc'})}"

    headers = {
        'Accept': 'application/vnd.github.preview.text-match+json',
        'User-Agent': 'qiri-bot/1.0'
    }

    try:
        res = requests.get(query_url, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"❌ GitHub request failed: {e}")
        return []

    results = []
    for item in data.get('items', [])[:max_results]:
        name = item.get('full_name')
        description = item.get('description') or ''
        url = item.get('html_url')
        language = item.get('language') or 'Unknown'
        stars = item.get('stargazers_count', 0)
        updated = parser.parse(item.get('updated_at') or item.get('created_at'))

        results.append({
            "title": name,
            "url": url,
            "snippet": f"{language} • ⭐ {stars} • {description}",
            "published": updated.strftime("%Y-%m-%d"),
        })

    return results

if __name__ == "__main__":
    query = "langchain"
    results = search_github_repos(query)
    print(results)
    # if not results:
    #     print("No results found.")
    # else:
    #     for i, r in enumerate(results, 1):
    #         print(f"{i}. {r['title']} ({r['published']})")
    #         print(f"   {r['url']}")
    #         print(f"   {r['snippet']}\n")

# use entities
# don't scrape