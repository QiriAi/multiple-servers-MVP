# SPDX-License-Identifier: AGPL-3.0-or-later
"""Simplified OpenStreetMap integration for chatbot."""

import requests
from urllib.parse import urlencode

def search_osm(query, language='en'):
    base_url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': query,
        'format': 'jsonv2',
        'addressdetails': 1,
        'extratags': 1,
        'dedupe': 1,
        'polygon_geojson': 1,
        'accept-language': language
    }

    headers = {
        'User-Agent': 'chatbot-search/1.0'
    }

    try:
        res = requests.get(base_url, params=urlencode(params), headers=headers, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print("❌ Error:", e)
        return []

def print_results(results):
    for i, result in enumerate(results, 1):
        title = result.get('display_name')
        lat = result.get('lat')
        lon = result.get('lon')
        osm_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=18"

        print(f"{i}. {title}\n   {osm_url}\n")

if __name__ == "__main__":
    query = "cafes in sydney australia"
    results = search_osm(query)
    print_results(results)

# BETTER SEARCH THEN APPLEMAPS