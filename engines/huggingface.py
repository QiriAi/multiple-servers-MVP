import requests
from datetime import datetime

def search_huggingface(query, endpoint='models', limit=5):
    base_url = "https://huggingface.co"
    api_url = f"{base_url}/api/{endpoint}?search={query}&limit={limit}&direction=-1"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Failed to fetch from Hugging Face: {e}")
        return

    print(f"\n🔎 Hugging Face {endpoint.capitalize()} Results for: '{query}'\n")
    for i, entry in enumerate(data[:limit], 1):
        item_url = f"{base_url}/{endpoint}/{entry['id']}" if endpoint != 'models' else f"{base_url}/{entry['id']}"
        title = entry['id']
        description = entry.get('description', 'No description provided.')
        likes = entry.get('likes', 0)
        downloads = entry.get('downloads', 0)
        tags = ', '.join(entry.get('tags', []))
        created = entry.get('createdAt')
        date_str = ""
        if created:
            try:
                date_str = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d")
            except:
                pass

        print(f"{i}. {title}")
        print(f"   🔗 Link: {item_url}")
        if description:
            print(f"   📄 Description: {description}")
        if tags:
            print(f"   🏷️ Tags: {tags}")
        print(f"   👍 Likes: {likes} | 📥 Downloads: {downloads} | 📅 Created: {date_str}")
        print("")

if __name__ == "__main__":
    #search_huggingface("whisper", endpoint="models")  # or datasets, spaces
    search_huggingface("house prices", endpoint="datasets")