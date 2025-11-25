import json
from app import app as flask_app


def get_tokens(client, email, password):
    r = client.post('/api/auth/login', json={'email': email, 'password': password})
    assert r.status_code == 200
    return r.get_json()['access_token'], r.get_json()['refresh_token']


def test_rating_and_review_crud():
    with flask_app.test_client() as c:
        # ensure a test user exists
        c.post('/api/auth/register', json={'username': 'tuser', 'email': 'tuser@example.dev', 'password': 'pw1234'})
        access, _ = get_tokens(c, 'tuser@example.dev', 'pw1234')

        headers = {'Authorization': f'Bearer {access}'}

        # create rating for existing seeded content mov-100
        resp = c.post('/api/content/mov-100/ratings', json={'score': 8}, headers=headers)
        assert resp.status_code in (200, 201)
        data = resp.get_json()
        assert 'rating' in data

        # create review
        resp = c.post('/api/content/mov-100/reviews', json={'body': 'Test review body'}, headers=headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert 'review' in data
        review_id = data['review']['id']

        # update review
        resp = c.put(f'/api/reviews/{review_id}', json={'body': 'Updated body'}, headers=headers)
        assert resp.status_code == 200

        # delete review
        resp = c.delete(f'/api/reviews/{review_id}', headers=headers)
        assert resp.status_code == 200
