import types

import backend.clients as clients


class _FakeResp:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status

    def json(self):
        return self._data


def test_tmdb_mapping_includes_runtime(monkeypatch):
    monkeypatch.setattr(clients, "_HAS_REQUESTS", True)
    monkeypatch.setattr(clients, "TMDB_KEY", "dummykey")

    def fake_get(url, params=None, timeout=None):
        if "search/movie" in url:
            return _FakeResp({"results": [{"id": 101, "title": "Test Movie", "release_date": "2020-01-01", "poster_path": "/p.jpg"}]})
        if "/movie/" in url:
            return _FakeResp({"id": 101, "runtime": 123})
        return _FakeResp({}, status=404)

    monkeypatch.setattr(clients, "requests", types.SimpleNamespace(get=fake_get))

    out = clients.search_tmdb_movies("whatever", limit=1)
    assert isinstance(out, list)
    assert len(out) == 1
    item = out[0]
    assert item["id"].startswith("mov-")
    assert item["title"] == "Test Movie"
    assert item["runtime_minutes"] == 123


def test_google_books_mapping_and_pagecount(monkeypatch):
    monkeypatch.setattr(clients, "_HAS_REQUESTS", True)
    monkeypatch.setattr(clients, "GOOGLE_BOOKS_KEY", "dummykey")

    def fake_get(url, params=None, timeout=None):
        if "volumes" in url:
            return _FakeResp({
                "items": [
                    {
                        "id": "bk-1",
                        "volumeInfo": {
                            "title": "Some Book",
                            "publishedDate": "2019-06-01",
                            "imageLinks": {"thumbnail": "http://img"},
                            "pageCount": 250,
                        },
                    }
                ]
            })
        return _FakeResp({}, status=404)

    import types as _types

    monkeypatch.setattr(clients, "requests", _types.SimpleNamespace(get=fake_get))

    out = clients.search_google_books("queryx", limit=1)
    assert isinstance(out, list)
    assert len(out) == 1
    b = out[0]
    assert b["id"].startswith("book-")
    assert b["title"] == "Some Book"
    assert b["page_count"] == 250

