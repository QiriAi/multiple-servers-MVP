import requests
from datetime import datetime

BASE_URL = "https://huggingface.co"
ENDPOINTS = ["models", "datasets", "spaces"]
FETCH_LIMIT = 20  # pull more to sort properly
RETURN_TOP_N = 3  # final number of results per section

# can also sort by "likes"
def search_huggingface(query, sort_by="downloads", return_top_n=RETURN_TOP_N):
    results_by_type = {}

    for endpoint in ENDPOINTS:
        api_url = f"{BASE_URL}/api/{endpoint}?search={query}&limit={FETCH_LIMIT}&direction=-1"

        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"❌ Failed to fetch from Hugging Face {endpoint}: {e}")
            continue

        formatted = []
        for entry in data:
            item_url = f"{BASE_URL}/{endpoint}/{entry['id']}" if endpoint != 'models' else f"{BASE_URL}/{entry['id']}"
            created = entry.get('createdAt')
            try:
                created_dt = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%fZ") if created else None
            except:
                created_dt = None

            formatted.append({
                #"id": entry['id'],
                "title": entry['id'],
                "description": entry.get("description", "No description provided."),
                #"tags": entry.get("tags", []),
                #"likes": entry.get("likes", 0),
                #"downloads": entry.get("downloads", 0),
                #"created": created_dt,
                "url": item_url
            })

        # Sort and truncate
        sorted_results = sorted(formatted, key=lambda x: x.get(sort_by, 0), reverse=True)
        results_by_type[endpoint] = sorted_results[:return_top_n]

    return results_by_type

# Example usage
if __name__ == "__main__":
    #data = search_huggingface("whisper", sort_by="downloads")
    data = search_huggingface("housing prices")
    print(data)


# use entities
# don't scrape