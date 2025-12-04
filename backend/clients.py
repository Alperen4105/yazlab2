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
from dotenv import load_dotenv

TMDB_KEY = os.getenv("TMDB_API_KEY")
GOOGLE_BOOKS_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_DETAILS_URL = "https://api.themoviedb.org/3/movie/{id}"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
OPENLIB_SEARCH_URL = "https://openlibrary.org/search.json"

# Simple in-memory TTL cache and basic per-provider rate limiter (dev-only)
_CACHE: Dict[str, Dict] = {}
# cache entry: {key: (expires_at_ts, value)}

import time

_DEFAULT_CACHE_TTL = int(os.getenv("CLIENT_CACHE_TTL", "300"))

# rate limiter state
_RATE = {
    "tmdb": {"window_start": 0, "count": 0, "limit": int(os.getenv("TMDB_RATE_LIMIT_PER_MIN", "60"))},
    "google": {"window_start": 0, "count": 0, "limit": int(os.getenv("GOOGLE_RATE_LIMIT_PER_MIN", "60"))},
}


def _cache_get(key: str):
    ent = _CACHE.get(key)
    now = time.time()
    if not ent:
        return None
    expires, val = ent
    if now >= expires:
        _CACHE.pop(key, None)
        return None
    return val


def _cache_set(key: str, value, ttl: Optional[int] = None):
    ttl = ttl or _DEFAULT_CACHE_TTL
    _CACHE[key] = (time.time() + ttl, value)


def _rate_allow(provider: str) -> bool:
    """Basic per-minute rate limiter. Returns True if request allowed, False if over limit."""
    state = _RATE.get(provider)
    if state is None:
        return True
    now = int(time.time())
    window = now // 60
    if state["window_start"] != window:
        state["window_start"] = window
        state["count"] = 0
    if state["count"] >= state["limit"]:
        return False
    state["count"] += 1
    return True


def _reload_env_if_needed():
    # ensure .env is loaded into os.environ in dev; safe no-op if already loaded
    try:
        load_dotenv(override=False)
    except Exception:
        pass


def search_tmdb_movies(query: str, limit: int = 10) -> List[Dict]:
    # Re-check API key at call time so .env can be added without restarting the process
    _reload_env_if_needed()
    local_key = TMDB_KEY or os.getenv("TMDB_API_KEY")
    # If API key or requests library is missing, return empty list gracefully
    if not local_key or not _HAS_REQUESTS:
        return []
    # allow using cache and rate-limit (check before outbound request)
    cache_key = f"tmdb:search:{query}:{limit}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    if not _rate_allow("tmdb"):
        return []
    params = {"query": query, "page": 1}
    try:
        r = requests.get(TMDB_SEARCH_URL, params={**params, "api_key": local_key}, timeout=5)
        if r.status_code != 200:
            return []
        data = r.json()
    except Exception as e:
        # Connection error, timeout, or JSON parse error — return empty list gracefully
        import sys
        print(f"[TMDb Search Error] {type(e).__name__}: {e}", file=sys.stderr)
        return []
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
            dr = requests.get(details_url, params={"api_key": local_key}, timeout=4)
            if dr.status_code == 200:
                ddata = dr.json()
                mapped["runtime_minutes"] = ddata.get("runtime")
                mapped["extra_details"] = ddata
        except Exception:
            # ignore details errors
            pass
        results.append(mapped)
    # write to cache so subsequent calls are fast
    _cache_set(cache_key, results)
    return results


def search_google_books(query: str, limit: int = 10) -> List[Dict]:
    # use Google Books if key present, else fallback to Open Library
    _reload_env_if_needed()
    local_gkey = GOOGLE_BOOKS_KEY or os.getenv("GOOGLE_BOOKS_API_KEY")
    cache_key = f"google:search:{query}:{limit}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    if local_gkey and _HAS_REQUESTS:
        if not _rate_allow("google"):
            return []
        params = {"q": query, "maxResults": limit}
        try:
            r = requests.get(GOOGLE_BOOKS_URL, params={**params, "key": local_gkey}, timeout=5)
            if r.status_code != 200:
                return []
            data = r.json()
        except Exception as e:
            # Connection error, timeout, or JSON parse error — fall through to Open Library
            import sys
            print(f"[Google Books Search Error] {type(e).__name__}: {e}", file=sys.stderr)
            # fall through to Open Library fallback
            data = None
        
        if data:
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
            # store the search results in cache
            _cache_set(cache_key, out)
            return out

    # fallback: Open Library
    params = {"q": query, "limit": limit}
    if not _HAS_REQUESTS:
        return []
    try:
        r = requests.get(OPENLIB_SEARCH_URL, params=params, timeout=5)
        if r.status_code != 200:
            return []
        data = r.json()
    except Exception as e:
        # Connection error, timeout, or JSON parse error — return empty list gracefully
        import sys
        print(f"[OpenLibrary Search Error] {type(e).__name__}: {e}", file=sys.stderr)
        return []
    
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


def get_tmdb_movie_details(external_id: str) -> Optional[Dict]:
    """Fetch TMDb movie details by external id like 'mov-438631' and return mapped dict.

    Returns None if requests/key missing or fetch fails.
    """
    _reload_env_if_needed()
    local_key = TMDB_KEY or os.getenv("TMDB_API_KEY")
    if not local_key or not _HAS_REQUESTS:
        return None
    cache_key = f"tmdb:detail:{external_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    if not _rate_allow("tmdb"):
        return None

    try:
        # extract numeric id
        if external_id.startswith("mov-"):
            mid = external_id.split("mov-", 1)[1]
        else:
            mid = external_id
        url = TMDB_DETAILS_URL.format(id=mid)
        r = requests.get(url, params={"api_key": local_key}, timeout=5)
        if r.status_code != 200:
            return None
        d = r.json()
        mapped = {
            "id": f"mov-{d.get('id')}",
            "external_id": f"mov-{d.get('id')}",
            "title": d.get("title"),
            "year": d.get("release_date", "")[:4] if d.get("release_date") else None,
            "poster": TMDB_IMAGE_BASE + d.get("poster_path") if d.get("poster_path") else None,
            "kind": "film",
            "runtime_minutes": d.get("runtime"),
            "extra": d,
        }
        _cache_set(cache_key, mapped)
        return mapped
    except Exception:
        return None


def get_book_details(external_id: str) -> Optional[Dict]:
    """Fetch book details by external_id (book-<googleId> or book-<openlib key>)

    If it's a Google Books id, use the volumes endpoint. If it's an OpenLibrary key
    (starts with '/'), fetch the OpenLibrary JSON. Returns mapping similar to search.
    """
    _reload_env_if_needed()
    local_gkey = GOOGLE_BOOKS_KEY or os.getenv("GOOGLE_BOOKS_API_KEY")
    if not _HAS_REQUESTS:
        return None
    cache_key = f"book:detail:{external_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    bid = external_id.split("book-", 1)[1] if external_id.startswith("book-") else external_id
    # Google Books volumes
    try:
        if local_gkey and not bid.startswith("/"):
            if not _rate_allow("google"):
                return None
            url = f"{GOOGLE_BOOKS_URL}/{bid}"
            r = requests.get(url, params={"key": local_gkey}, timeout=5)
            if r.status_code == 200:
                data = r.json()
                vi = data.get("volumeInfo", {})
                mapped = {
                    "id": f"book-{data.get('id')}",
                    "external_id": f"book-{data.get('id')}",
                    "title": vi.get("title"),
                    "year": vi.get("publishedDate", "")[:4] if vi.get("publishedDate") else None,
                    "poster": vi.get("imageLinks", {}).get("thumbnail"),
                    "kind": "book",
                    "page_count": vi.get("pageCount"),
                    "extra": vi,
                }
                _cache_set(cache_key, mapped)
                return mapped
        # else fallback to OpenLibrary (key begins with '/') or no google key
        if bid.startswith("/"):
            url = f"https://openlibrary.org{bid}.json"
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                d = r.json()
                title = d.get("title")
                year = d.get("first_publish_date") or d.get("created", {}).get("value")
                mapped = {
                    "id": f"book-{bid}",
                    "external_id": f"book-{bid}",
                    "title": title,
                    "year": year[:4] if year else None,
                    "poster": None,
                    "kind": "book",
                    "page_count": None,
                    "extra": d,
                }
                _cache_set(cache_key, mapped)
                return mapped
    except Exception:
        return None
    return None