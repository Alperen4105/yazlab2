import types

import backend.clients as clients


class _FakeResp:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status

    def json(self):
        return self._data


def _reset_state():
    # clear in-memory caches and reset counters
    clients._CACHE.clear()
    for k in clients._RATE:
        clients._RATE[k]["window_start"] = 0
        clients._RATE[k]["count"] = 0


def test_tmdb_search_is_cached(monkeypatch):
    monkeypatch.setattr(clients, "_HAS_REQUESTS", True)
    monkeypatch.setattr(clients, "TMDB_KEY", "dummykey")
    _reset_state()

    calls = []

    def fake_get(url, params=None, timeout=None):
        calls.append(url)
        if "search/movie" in url:
            return _FakeResp({"results": [{"id": 101, "title": "Cached Movie", "release_date": "2020-01-01", "poster_path": "/p.jpg"}]})
        if "/movie/" in url:
            return _FakeResp({"id": 101, "runtime": 90})
        return _FakeResp({}, status=404)

    monkeypatch.setattr(clients, "requests", types.SimpleNamespace(get=fake_get))

    out1 = clients.search_tmdb_movies("whatever", limit=1)
    assert isinstance(out1, list) and len(out1) == 1
    assert calls, "requests.get should be called on first search"

    before = len(calls)
    out2 = clients.search_tmdb_movies("whatever", limit=1)
    assert out1 == out2
    # second call should be served from cache -> no new calls
    assert len(calls) == before


def test_tmdb_details_cached(monkeypatch):
    monkeypatch.setattr(clients, "_HAS_REQUESTS", True)
    monkeypatch.setattr(clients, "TMDB_KEY", "dummykey")
    _reset_state()

    calls = []

    def fake_get(url, params=None, timeout=None):
        calls.append(url)
        if "/movie/" in url:
            return _FakeResp({"id": 202, "title": "Detail Movie", "release_date": "2018-01-01", "runtime": 77})
        return _FakeResp({}, status=404)

    monkeypatch.setattr(clients, "requests", types.SimpleNamespace(get=fake_get))

    out1 = clients.get_tmdb_movie_details("mov-202")
    assert isinstance(out1, dict) and out1.get("id") == "mov-202"

    before = len(calls)
    out2 = clients.get_tmdb_movie_details("mov-202")
    assert out1 == out2
    # cached -> no new external call
    assert len(calls) == before


def test_google_search_is_cached(monkeypatch):
    monkeypatch.setattr(clients, "_HAS_REQUESTS", True)
    monkeypatch.setattr(clients, "GOOGLE_BOOKS_KEY", "dummykey")
    _reset_state()

    calls = []

    def fake_get(url, params=None, timeout=None):
        calls.append(url)
        if "volumes" in url:
            return _FakeResp({
                "items": [
                    {
                        "id": "bk-1",
                        "volumeInfo": {"title": "Cached Book", "publishedDate": "2019-06-01", "pageCount": 123},
                    }
                ]
            })
        return _FakeResp({}, status=404)

    monkeypatch.setattr(clients, "requests", types.SimpleNamespace(get=fake_get))

    out1 = clients.search_google_books("queryx", limit=1)
    assert isinstance(out1, list) and len(out1) == 1

    before = len(calls)
    out2 = clients.search_google_books("queryx", limit=1)
    assert out1 == out2
    assert len(calls) == before
