"""Quick test to verify TMDb API is working"""
import os
from dotenv import load_dotenv
load_dotenv()

import requests

api_key = os.getenv('TMDB_API_KEY')
print("Testing TMDb API...")
print(f"API Key: {api_key[:10]}..." if api_key else "No API Key")
print()

# Direct API test
print("Testing direct TMDb API call...")
url = "https://api.themoviedb.org/3/search/movie"
params = {"api_key": api_key, "query": "batman", "page": 1}
try:
    r = requests.get(url, params=params, timeout=5)
    print(f"Status: {r.status_code}")
    print(f"URL: {r.url}")
    if r.status_code == 200:
        data = r.json()
        print(f"Total results: {data.get('total_results')}")
        results = data.get('results', [])[:3]
        for item in results:
            print(f"  - {item.get('title')} ({item.get('release_date', 'N/A')[:4]})")
    else:
        print(f"Error: {r.text[:500]}")
except Exception as e:
    print(f"Exception: {e}")
print()

# Now test through our client
from backend.clients import search_tmdb_movies
print("Testing search_tmdb_movies('batman'):")
results = search_tmdb_movies("batman", limit=3)
print(f"Results: {len(results) if results else 0}")
if results:
    for r in results:
        print(f"  - {r.get('title')} ({r.get('year')}) - ID: {r.get('id')}")

