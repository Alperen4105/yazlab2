from app import app as flask_app


def test_follow_and_feed_filter():
    with flask_app.test_client() as c:
        # create two users
        c.post('/api/auth/register', json={'username': 'alice', 'email': 'alice@example.dev', 'password': 'pw1234'})
        c.post('/api/auth/register', json={'username': 'bob', 'email': 'bob@example.dev', 'password': 'pw1234'})

        # bob posts a review so he has an activity
        r = c.post('/api/auth/login', json={'email':'bob@example.dev','password':'pw1234'})
        bob_token = r.get_json().get('access_token')
        headers_bob = {'Authorization': f'Bearer {bob_token}'}
        c.post('/api/content/mov-100/reviews', json={'body': 'bob review'}, headers=headers_bob)

        # alice follows bob
        r = c.post('/api/auth/login', json={'email':'alice@example.dev','password':'pw1234'})
        alice_token = r.get_json().get('access_token')
        headers_alice = {'Authorization': f'Bearer {alice_token}'}
        resp = c.post('/api/users/bob/follow', headers=headers_alice)
        assert resp.status_code == 201

        # alice fetches feed and should see bob's activity
        resp = c.get('/api/feed', headers=headers_alice)
        data = resp.get_json()
        assert resp.status_code == 200
        items = data.get('items', [])
        assert any(item['user']['username'] == 'bob' for item in items)
