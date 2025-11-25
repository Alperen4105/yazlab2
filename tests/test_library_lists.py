from app import app as flask_app


def test_library_and_list_endpoints():
    with flask_app.test_client() as c:
        # register + login
        c.post('/api/auth/register', json={'username': 'luvuser', 'email': 'luvuser@example.dev', 'password': 'pw1234'})
        r = c.post('/api/auth/login', json={'email':'luvuser@example.dev','password':'pw1234'})
        access = r.get_json().get('access_token')
        headers = {'Authorization': f'Bearer {access}'}

        # add library
        resp = c.post('/api/content/mov-100/library', json={'status':'watchlist'}, headers=headers)
        assert resp.status_code == 201

        # remove
        resp = c.delete('/api/content/mov-100/library', headers=headers)
        assert resp.status_code == 200

        # create list and add item
        resp = c.post('/api/lists', json={'title':'My List'}, headers=headers)
        assert resp.status_code == 201
        list_id = resp.get_json().get('id')
        resp = c.post(f'/api/lists/{list_id}/items', json={'content_id':'mov-100'}, headers=headers)
        assert resp.status_code == 201
