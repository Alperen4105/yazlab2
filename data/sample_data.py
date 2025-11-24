"""Static placeholder data to mimic backend responses while UI is designed."""

from __future__ import annotations

FEED_ACTIVITIES = [
    {
        "id": "act-001",
        "user": {
            "username": "elifkara",
            "name": "Elif Kara",
            "avatar": "https://i.pravatar.cc/80?img=47",
        },
        "type": "rating",
        "content": {
            "id": "mov-100",
            "title": "Dune: Part Two",
            "year": 2024,
            "poster": "https://image.tmdb.org/t/p/w500/8bcoRX3hQRHufLPSDREdvr3YMXx.jpg",
            "kind": "film",
        },
        "score": 9,
        "comment": None,
        "timestamp": "3 saat önce",
        "likes": 18,
        "comments": 4,
    },
    {
        "id": "act-002",
        "user": {
            "username": "ozgurbakir",
            "name": "Özgür Bakır",
            "avatar": "https://i.pravatar.cc/80?img=52",
        },
        "type": "review",
        "content": {
            "id": "book-200",
            "title": "Project Hail Mary",
            "year": 2021,
            "poster": "https://covers.openlibrary.org/b/id/11829038-L.jpg",
            "kind": "book",
        },
        "score": 8,
        "comment": "Bilimsel detaylarla dolu hızlı tempolu bir macera. Andy Weir yine mizahı eksik etmemiş.",
        "timestamp": "5 saat önce",
        "likes": 11,
        "comments": 6,
    },
    {
        "id": "act-003",
        "user": {
            "username": "selinay",
            "name": "Selin Aydın",
            "avatar": "https://i.pravatar.cc/80?img=15",
        },
        "type": "list_add",
        "content": {
            "id": "mov-300",
            "title": "Past Lives",
            "year": 2023,
            "poster": "https://image.tmdb.org/t/p/w500/kGk5lS4NqQNzQXtXdeVJ0bjjC5o.jpg",
            "kind": "film",
        },
        "list_name": "En İyi Festival Filmleri",
        "timestamp": "1 gün önce",
        "likes": 7,
        "comments": 2,
    },
]

POPULAR_CONTENT = {
    "top_rated": [
        {
            "id": "mov-120",
            "title": "Poor Things",
            "poster": "https://image.tmdb.org/t/p/w342/qV1aXq6lWcv16O3MH8b6wR8hDnV.jpg",
            "score": 8.7,
            "kind": "film",
        },
        {
            "id": "book-300",
            "title": "The Three-Body Problem",
            "poster": "https://covers.openlibrary.org/b/id/9251973-M.jpg",
            "score": 9.1,
            "kind": "book",
        },
    ],
    "most_discussed": [
        {
            "id": "mov-130",
            "title": "Inside Out 2",
            "poster": "https://image.tmdb.org/t/p/w342/jfuvuPL6NG7F8CN8SB2wJMgn7NN.jpg",
            "comments": 132,
            "kind": "film",
        },
        {
            "id": "book-310",
            "title": "Fourth Wing",
            "poster": "https://covers.openlibrary.org/b/id/13214731-M.jpg",
            "comments": 98,
            "kind": "book",
        },
    ],
}

FEATURED_LISTS = [
    {
        "id": "list-001",
        "owner": "elifkara",
        "title": "Karanlık Bilimkurgu Seçkisi",
        "items": 24,
    },
    {
        "id": "list-002",
        "owner": "selinay",
        "title": "Oscar Adayı Filmler (2020-2025)",
        "items": 32,
    },
]

FEATURED_USERS = [
    {"username": "elifkara", "name": "Elif Kara"},
    {"username": "ozgurbakir", "name": "Özgür Bakır"},
    {"username": "selinay", "name": "Selin Aydın"},
]

LIBRARY_TABS = {
    "watched": [
            {"title": "Oppenheimer", "year": 2023, "poster": "https://image.tmdb.org/t/p/w185/bP4ufNPw3VOCFabaN6BuAdcIoxe.jpg"},
            {"title": "Barbie", "year": 2023, "poster": "https://image.tmdb.org/t/p/w185/cImwv69n5s86vQZBdY3KFf1JQVE.jpg"},
    ],
    "watchlist": [
            {"title": "The Boy and the Heron", "year": 2024, "poster": "https://image.tmdb.org/t/p/w185/ktHEdqmMWC1wdfPRMRCTZe2OISL.jpg"},
    ],
    "read": [
            {"title": "Atomic Habits", "year": 2018, "poster": "https://covers.openlibrary.org/b/id/9252064-M.jpg"},
    ],
    "reading_list": [
            {"title": "The Midnight Library", "year": 2020, "poster": "https://covers.openlibrary.org/b/id/10532476-M.jpg"},
    ],
}

USER_PROFILES = {
    "elifkara": {
        "username": "elifkara",
        "name": "Elif Kara",
        "avatar": "https://i.pravatar.cc/160?img=47",
        "bio": "Bilimkurgu ve arthouse sinemaya tutkun ürün yöneticisi.",
        "followers": 321,
        "following": 148,
    },
    "ozgurbakir": {
        "username": "ozgurbakir",
        "name": "Özgür Bakır",
        "avatar": "https://i.pravatar.cc/160?img=52",
        "bio": "Tam zamanlı veri bilimci, yarı zamanlı kitap kurdu.",
        "followers": 210,
        "following": 98,
    },
}

