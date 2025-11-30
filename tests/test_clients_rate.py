import types
import time

import backend.clients as clients


class _FakeResp:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status

    def json(self):
        return self._data


def _reset_state():
    clients._CACHE.clear()
    for k in clients._RATE:
        clients._RATE[k]["window_start"] = 0
        clients._RATE[k]["count"] = 0


def test_tmdb_rate_limit_blocks(monkeypatch):
    monkeypatch.setattr(clients, "_HAS_REQUESTS", True)
    monkeypatch.setattr(clients, "TMDB_KEY", "dummykey")
    _reset_state()

    # ensure we operate inside the same minute window
    now_window = int(time.time()) // 60
    clients._RATE["tmdb"]["window_start"] = now_window
    clients._RATE["tmdb"]["count"] = 0
    clients._RATE["tmdb"]["limit"] = 1

    calls = []

    def fake_get(url, params=None, timeout=None):
        calls.append(url)
        if "search/movie" in url:
            return _FakeResp({"results": [{"id": 9001, "title": "R Limit", "release_date": "2020-01-01"}]})
        if "/movie/" in url:
            return _FakeResp({"id": 9001, "runtime": 60})
        return _FakeResp({}, status=404)

    monkeypatch.setattr(clients, "requests", types.SimpleNamespace(get=fake_get))

    # first call consumes the single allowed request
    res1 = clients.search_tmdb_movies("rlimit", limit=1)
    assert isinstance(res1, list) and len(res1) == 1

    # second call will be served from cache (so still returns the item)
    prev = len(calls)
    res2 = clients.search_tmdb_movies("rlimit", limit=1)
    assert res2 == res1
    assert len(calls) == prev

    # if cache is cleared and we try again within the same window it should be blocked
    clients._CACHE.clear()
    prev = len(calls)
    res3 = clients.search_tmdb_movies("rlimit", limit=1)
    assert res3 == []
    assert len(calls) == prev


def test_google_rate_limit_blocks(monkeypatch):
    monkeypatch.setattr(clients, "_HAS_REQUESTS", True)
    monkeypatch.setattr(clients, "GOOGLE_BOOKS_KEY", "dummykey")
    _reset_state()

    now_window = int(time.time()) // 60
    clients._RATE["google"]["window_start"] = now_window
    clients._RATE["google"]["count"] = 0
    clients._RATE["google"]["limit"] = 1

    calls = []

    def fake_get(url, params=None, timeout=None):
        calls.append(url)
        if "volumes" in url:
            return _FakeResp({"items": [{"id": "g1", "volumeInfo": {"title": "G Limit", "pageCount": 10}}]})
        return _FakeResp({}, status=404)

    monkeypatch.setattr(clients, "requests", types.SimpleNamespace(get=fake_get))

    # first call allowed
    res1 = clients.search_google_books("glimit", limit=1)
    assert isinstance(res1, list) and len(res1) == 1

    prev = len(calls)
    # second call still hits the cache and returns the same thing
    res2 = clients.search_google_books("glimit", limit=1)
    assert res2 == res1
    assert len(calls) == prev

    # clear cache -> rate limiter blocks further outbound calls
    clients._CACHE.clear()
    prev = len(calls)
    res3 = clients.search_google_books("glimit", limit=1)
    assert res3 == []
    assert len(calls) == prev
