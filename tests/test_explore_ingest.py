from app import app as flask_app
from backend.extensions import db
from backend.models import Content
import backend.clients as clients


def test_explore_ingests_external_and_is_idempotent(monkeypatch):
    # snapshot existing contents so we can restore them after the test (test isolation)
    with flask_app.app_context():
        orig = [
            {
                "external_id": c.external_id,
                "content_type": c.content_type,
                "title": c.title,
                "synopsis": c.synopsis,
                "release_year": c.release_year,
                "runtime_minutes": c.runtime_minutes,
                "page_count": c.page_count,
                "cover_url": c.cover_url,
                "extra_metadata": c.extra_metadata,
            }
            for c in Content.query.all()
        ]
        Content.query.delete()
        db.session.commit()

    # prepare fake client results
    movie = {
        "external_id": "mov-test-1",
        "id": "mov-test-1",
        "title": "External Movie",
        "year": "2022",
        "poster": "http://img.mov",
        "kind": "film",
        "runtime_minutes": 100,
        "extra": {},
    }
    book = {
        "external_id": "book-test-1",
        "id": "book-test-1",
        "title": "External Book",
        "year": "2019",
        "poster": None,
        "kind": "book",
        "page_count": 300,
        "extra": {},
    }

    # api_explore imported the helper functions at module import time, so patch them there
    import backend.api as api
    monkeypatch.setattr(api, "search_tmdb_movies", lambda q, limit=10: [movie])
    monkeypatch.setattr(api, "search_google_books", lambda q, limit=10: [book])

    with flask_app.test_client() as client:
        # first call should ingest
        r = client.get("/api/explore?q=testquery")
        assert r.status_code == 200
        data = r.get_json()
        assert data and data.get("count", 0) >= 2

        # check DB has entries
        with flask_app.app_context():
            m = Content.query.filter_by(external_id="mov-test-1").first()
            b = Content.query.filter_by(external_id="book-test-1").first()
            assert m is not None and m.content_type == "movie"
            assert b is not None and b.content_type == "book"
            initial_count = Content.query.count()

        # second call should not create duplicates (idempotent)
        r2 = client.get("/api/explore?q=testquery")
        assert r2.status_code == 200
        with flask_app.app_context():
            assert Content.query.count() == initial_count

            # cleanup - remove test-created contents
            Content.query.filter_by(external_id="mov-test-1").delete()
            Content.query.filter_by(external_id="book-test-1").delete()
            db.session.commit()

            # restore original snapshot so other tests don't observe missing data
            for c in orig:
                cc = Content(
                    external_id=c.get("external_id"),
                    content_type=c.get("content_type") or "movie",
                    title=c.get("title") or "Untitled",
                    synopsis=c.get("synopsis"),
                    release_year=c.get("release_year"),
                    runtime_minutes=c.get("runtime_minutes"),
                    page_count=c.get("page_count"),
                    cover_url=c.get("cover_url"),
                    extra_metadata=c.get("extra_metadata"),
                )
                db.session.add(cc)
            db.session.commit()


def test_explore_calls_external_when_db_populated_but_no_match(monkeypatch):
    # Ensure there are some existing contents that don't match the query
    from app import app as flask_app
    from backend.extensions import db
    from backend.models import Content

    with flask_app.app_context():
        # ensure DB contains at least one unrelated entry
        Content.query.delete()
        c = Content(external_id='mov-999', content_type='movie', title='Some Movie', cover_url=None)
        db.session.add(c)
        db.session.commit()

    movie = {
        "external_id": "mov-external-1",
        "id": "mov-external-1",
        "title": "External Movie",
        "year": "2022",
        "poster": "http://img.mov",
        "kind": "film",
        "runtime_minutes": 100,
        "extra": {},
    }
    # patch api module functions (api imports clients at top)
    import backend.api as api
    monkeypatch.setattr(api, "search_tmdb_movies", lambda q, limit=10: [movie])
    monkeypatch.setattr(api, "search_google_books", lambda q, limit=10: [])

    with flask_app.test_client() as client:
        r = client.get('/api/explore?q=External+Movie')
        assert r.status_code == 200
        data = r.get_json()
        # external result should be included
        assert data and data.get('count', 0) >= 1

    # cleanup
    with flask_app.app_context():
        Content.query.filter_by(external_id='mov-external-1').delete()
        Content.query.filter_by(external_id='mov-999').delete()
        db.session.commit()
