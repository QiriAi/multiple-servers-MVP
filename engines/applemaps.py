### This script scrapes DuckDuckGo's apple maps integration to search locations without api key

import requests
from urllib.parse import urlencode
from time import time
from json import loads

# Token cache for re-use
token_cache = {"value": None, "last_updated": 0}

def get_mapkit_token():
    """Obtain access token for Apple MapKit using DuckDuckGo public token."""
    now = int(time())
    if token_cache["value"] and now - token_cache["last_updated"] < 1800:
        return token_cache["value"]
    
    try:
        # Step 1: Get bearer token from DuckDuckGo
        token_res = requests.get('https://duckduckgo.com/local.js?get_mk_token=1', timeout=5)
        token_res.raise_for_status()
        duck_token = token_res.text.strip()

        # Step 2: Get actual MapKit token
        auth_res = requests.get(
            'https://cdn.apple-mapkit.com/ma/bootstrap?apiVersion=2&mkjsVersion=5.72.53&poi=1',
            headers={'Authorization': f'Bearer {duck_token}'},
            timeout=5
        )
        auth_res.raise_for_status()
        apple_token = loads(auth_res.text)["authInfo"]["access_token"]
        
        # Cache it
        token_cache["value"] = apple_token
        token_cache["last_updated"] = now
        return apple_token
    except Exception as e:
        print(f"❌ Failed to obtain Apple MapKit token: {e}")
        return None


def search_apple_maps(query, lang="en"):
    token = get_mapkit_token()
    if not token:
        return []

    url = f"https://api.apple-mapkit.com/v1/search?{urlencode({'q': query, 'lang': lang})}&mkjsVersion=5.72.53"
    try:
        res = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return []

    results = []
    for result in data.get("results", []):
        title = result.get("name", "")
        place_url = result.get("placecardUrl", "")
        lat = result.get("center", {}).get("lat")
        lng = result.get("center", {}).get("lng")
        address_parts = [
            result.get("subThoroughfare"),
            result.get("thoroughfare"),
            result.get("locality"),
            result.get("postCode"),
            result.get("country")
        ]
        address = ", ".join([p for p in address_parts if p])

        results.append({
            "title": title,
            "url": place_url,
            "snippet": f"{address} (Lat: {lat}, Lng: {lng})"
        })

    return results


# Standalone test
if __name__ == "__main__":
    query = "yo-chi"
    results = search_apple_maps(query)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['title']}\n   {r['url']}\n   {r['snippet']}\n")

"""
queries i tried with bad results
- coffee near sydney --> returned sydney
- yochi, sydney, australia --> returned sydney
- duo duo ice cream australia -->  returned 17 results all ice cream in australia include duo duo but not specific
- ice cream australia --> returned only 2 results
- duoduo australia --> returned 1 result
- ice cream roselands australia --> returns roselands 
- woolworths kingsgrove australia --> returns kingsgrove
- thai food sydney australia --> returned sydney
- thai food --> returned a place called "thai food" in germany

good queries (but limited results):
- woolworths australia
- yochi frozen yogurt australia
- thai food australia --> returned 1 result (has the name australia in it "paste australia")

good! (i searched as appeared on the search engine) BE ACCURATE!!!
- yo-chi newtown
- duo duo strathfield
- time for thai kingsford --> correct returned for "It's time for thai"
- it's time for thai --> returns the 3 locations in newtown, haymarket and kingsford
- yo-chi --> returned their 6 branches
[ doesn't work for duo duo which must have stores with similar names across the world ]
"""