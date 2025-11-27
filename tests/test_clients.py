import backend.clients as clients


def test_clients_functions_exist_and_return_list():
    # In CI/dev without API keys and possibly without requests installed
    # the functions should still exist and return a list (maybe empty)
    assert hasattr(clients, "search_tmdb_movies")
    assert hasattr(clients, "search_google_books")

    res1 = clients.search_tmdb_movies("inception", limit=1)
    res2 = clients.search_google_books("python", limit=1)

    assert isinstance(res1, list)
    assert isinstance(res2, list)
