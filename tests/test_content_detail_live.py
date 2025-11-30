from app import app as flask_app
from backend.extensions import db
from backend.models import Content


def test_content_detail_movie_live(monkeypatch):
    # ensure DB doesn't have this external id
    with flask_app.app_context():
        Content.query.filter_by(external_id='mov-live-1').delete()
        db.session.commit()

    movie = {
        'id': 'mov-live-1',
        'external_id': 'mov-live-1',
        'title': 'Live Movie',
        'year': '2024',
        'poster': 'http://img',
        'kind': 'film',
        'runtime_minutes': 136,
        'extra': {},
    }

    import backend.api as api
    monkeypatch.setattr(api, 'get_tmdb_movie_details', lambda id: movie)

    with flask_app.test_client() as c:
        r = c.get('/api/content/mov-live-1')
        assert r.status_code == 200
        data = r.get_json()
        assert data and data.get('content')
        content = data['content']
        assert content.get('meta', {}).get('runtime_minutes') == 136

    # ensure not persisted by default
    with flask_app.app_context():
        assert Content.query.filter_by(external_id='mov-live-1').first() is None


def test_content_detail_book_live(monkeypatch):
    with flask_app.app_context():
        Content.query.filter_by(external_id='book-live-1').delete()
        db.session.commit()

    book = {
        'id': 'book-live-1',
        'external_id': 'book-live-1',
        'title': 'Live Book',
        'year': '2020',
        'poster': None,
        'kind': 'book',
        'page_count': 420,
        'extra': {},
    }

    import backend.api as api
    monkeypatch.setattr(api, 'get_book_details', lambda id: book)

    with flask_app.test_client() as c:
        r = c.get('/api/content/book-live-1')
        assert r.status_code == 200
        data = r.get_json()
        assert data and data.get('content')
        content = data['content']
        assert content.get('meta', {}).get('page_count') == 420

    with flask_app.app_context():
        assert Content.query.filter_by(external_id='book-live-1').first() is None
