"""Small wrappers for external content APIs (TMDb + Google Books/OpenLibrary).

These are intentionally minimal and synchronous — good enough for the project demo.
They look for environment variables TMDB_API_KEY and GOOGLE_BOOKS_API_KEY, otherwise
use Open Library for books.
"""
from __future__ import annotations

import os
try:
    import requests  # optional dev dependency
    _HAS_REQUESTS = True
except Exception:  # pragma: no cover - optional in minimal environments
    requests = None
    _HAS_REQUESTS = False
from typing import List, Dict, Optional

TMDB_KEY = os.getenv("TMDB_API_KEY")
GOOGLE_BOOKS_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_DETAILS_URL = "https://api.themoviedb.org/3/movie/{id}"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
OPENLIB_SEARCH_URL = "https://openlibrary.org/search.json"


def search_tmdb_movies(query: str, limit: int = 10) -> List[Dict]:
    # If API key or requests library is missing, return empty list gracefully
    if not TMDB_KEY or not _HAS_REQUESTS:
        return []
    params = {"api_key": TMDB_KEY, "query": query, "page": 1}
    r = requests.get(TMDB_SEARCH_URL, params=params, timeout=5)
    if r.status_code != 200:
        return []
    data = r.json()
    results = []
    for item in data.get("results", [])[:limit]:
        mapped = {
            "id": f"mov-{item.get('id')}",
            "external_id": f"mov-{item.get('id')}",
            "title": item.get("title"),
            "year": item.get("release_date", "")[:4] if item.get("release_date") else None,
            "poster": TMDB_IMAGE_BASE + item.get("poster_path") if item.get("poster_path") else None,
            "kind": "film",
            "extra": item,
            "runtime_minutes": None,
        }
        # optionally try to fetch details (runtime) when available
        try:
            details_url = TMDB_DETAILS_URL.format(id=item.get("id"))
            dr = requests.get(details_url, params={"api_key": TMDB_KEY}, timeout=4)
            if dr.status_code == 200:
                ddata = dr.json()
                mapped["runtime_minutes"] = ddata.get("runtime")
                mapped["extra_details"] = ddata
        except Exception:
            # ignore details errors
            pass
        results.append(mapped)
    return results


def search_google_books(query: str, limit: int = 10) -> List[Dict]:
    # use Google Books if key present, else fallback to Open Library
    if GOOGLE_BOOKS_KEY and _HAS_REQUESTS:
        params = {"q": query, "maxResults": limit, "key": GOOGLE_BOOKS_KEY}
        r = requests.get(GOOGLE_BOOKS_URL, params=params, timeout=5)
        if r.status_code != 200:
            return []
        data = r.json()
        out = []
        for item in data.get("items", [])[:limit]:
            vi = item.get("volumeInfo", {})
            external_id = item.get("id")
            out.append(
                {
                    "id": f"book-{external_id}",
                    "external_id": f"book-{external_id}",
                    "title": vi.get("title"),
                    "year": vi.get("publishedDate", "")[:4] if vi.get("publishedDate") else None,
                    "poster": vi.get("imageLinks", {}).get("thumbnail"),
                    "kind": "book",
                    "extra": vi,
                    "page_count": vi.get("pageCount"),
                }
            )
        return out

    # fallback: Open Library
    params = {"q": query, "limit": limit}
    if not _HAS_REQUESTS:
        return []
    r = requests.get(OPENLIB_SEARCH_URL, params=params, timeout=5)
    if r.status_code != 200:
        return []
    data = r.json()
    out = []
    for item in data.get("docs", [])[:limit]:
        ext_id = item.get("key")
        out.append(
            {
                "id": f"book-{ext_id}",
                "external_id": f"book-{ext_id}",
                "title": item.get("title"),
                "year": item.get("first_publish_year"),
                "poster": None,
                "kind": "book",
                "extra": item,
                "page_count": item.get("number_of_pages_median") or item.get("edition_count"),
            }
        )
    return out