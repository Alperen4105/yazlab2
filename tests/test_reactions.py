from app import app as flask_app


def test_review_reactions_and_activity_like():
    with flask_app.test_client() as c:
        # create user
        c.post('/api/auth/register', json={'username':'rxuser','email':'rxuser@example.dev','password':'pw1234'})
        r = c.post('/api/auth/login', json={'email':'rxuser@example.dev','password':'pw1234'})
        token = r.get_json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}

        # create a review
        r = c.post('/api/content/mov-100/reviews', json={'body': 'reaction test'}, headers=headers)
        assert r.status_code == 201
        review_id = r.get_json()['review']['id']

        # add like reaction
        r = c.post(f'/api/reviews/{review_id}/reactions', json={'reaction_type':'like'}, headers=headers)
        assert r.status_code == 201

        # duplicate reaction should 409
        r = c.post(f'/api/reviews/{review_id}/reactions', json={'reaction_type':'like'}, headers=headers)
        assert r.status_code == 409

        # remove reaction
        r = c.delete(f'/api/reviews/{review_id}/reactions', headers=headers)
        assert r.status_code == 200

        # activity like: find an activity for this review
        # create another review to ensure activity exists
        r = c.post('/api/content/mov-100/reviews', json={'body': 'activity like test'}, headers=headers)
        assert r.status_code == 201
        # list feed and get activity id
        r = c.get('/api/feed', headers=headers)
        items = r.get_json().get('items', [])
        assert len(items) > 0
        act = items[0]
        aid = int(act['id'].split('-')[-1])

        r = c.post(f'/api/activities/{aid}/like', headers=headers)
        assert r.status_code == 200
