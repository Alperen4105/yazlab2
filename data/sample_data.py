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
    {
        "id": "act-004",
        "user": {
            "username": "elifkara",
            "name": "Elif Kara",
            "avatar": "https://i.pravatar.cc/80?img=47",
        },
        "type": "rating",
        "content": {
            "id": "mov-101",
            "title": "Oppenheimer",
            "year": 2023,
            "poster": "https://image.tmdb.org/t/p/w500/bP4ufNPw3VOCFabaN6BuAdcIoxe.jpg",
            "kind": "film",
        },
        "score": 10,
        "comment": None,
        "timestamp": "2 gün önce",
        "likes": 32,
        "comments": 12,
    },
    {
        "id": "act-005",
        "user": {
            "username": "ozgurbakir",
            "name": "Özgür Bakır",
            "avatar": "https://i.pravatar.cc/80?img=52",
        },
        "type": "review",
        "content": {
            "id": "book-201",
            "title": "The Three-Body Problem",
            "year": 2008,
            "poster": "https://covers.openlibrary.org/b/id/9251973-L.jpg",
            "kind": "book",
        },
        "score": 9,
        "comment": "Çağdaş bilimkurgunun başyapıtlarından biri. Fizik ve felsefe bir araya gelmiş.",
        "timestamp": "3 gün önce",
        "likes": 24,
        "comments": 8,
    },
    {
        "id": "act-006",
        "user": {
            "username": "selinay",
            "name": "Selin Aydın",
            "avatar": "https://i.pravatar.cc/80?img=15",
        },
        "type": "rating",
        "content": {
            "id": "mov-301",
            "title": "Poor Things",
            "year": 2023,
            "poster": "https://image.tmdb.org/t/p/w500/qV1aXq6lWcv16O3MH8b6wR8hDnV.jpg",
            "kind": "film",
        },
        "score": 8,
        "comment": None,
        "timestamp": "4 gün önce",
        "likes": 15,
        "comments": 5,
    },
    {
        "id": "act-007",
        "user": {
            "username": "elifkara",
            "name": "Elif Kara",
            "avatar": "https://i.pravatar.cc/80?img=47",
        },
        "type": "review",
        "content": {
            "id": "mov-102",
            "title": "Killers of the Flower Moon",
            "year": 2023,
            "poster": "https://image.tmdb.org/t/p/w500/dB6Krk806zeqd0YNp2ngQ9zXteH.jpg",
            "kind": "film",
        },
        "score": 9,
        "comment": "Scorsese'nin tarihsel trajedi anlatımı mükemmel. DiCaprio ve De Niro harika.",
        "timestamp": "5 gün önce",
        "likes": 28,
        "comments": 10,
    },
    {
        "id": "act-008",
        "user": {
            "username": "ozgurbakir",
            "name": "Özgür Bakır",
            "avatar": "https://i.pravatar.cc/80?img=52",
        },
        "type": "list_add",
        "content": {
            "id": "book-202",
            "title": "Atomic Habits",
            "year": 2018,
            "poster": "https://covers.openlibrary.org/b/id/9252064-L.jpg",
            "kind": "book",
        },
        "list_name": "Kişisel Gelişim Klasikleri",
        "timestamp": "6 gün önce",
        "likes": 12,
        "comments": 3,
    },
    {
        "id": "act-009",
        "user": {
            "username": "selinay",
            "name": "Selin Aydın",
            "avatar": "https://i.pravatar.cc/80?img=15",
        },
        "type": "rating",
        "content": {
            "id": "mov-302",
            "title": "The Boy and the Heron",
            "year": 2023,
            "poster": "https://image.tmdb.org/t/p/w500/ktHEdqmMWC1wdfPRMRCTZe2OISL.jpg",
            "kind": "film",
        },
        "score": 10,
        "comment": None,
        "timestamp": "1 hafta önce",
        "likes": 41,
        "comments": 15,
    },
    {
        "id": "act-010",
        "user": {
            "username": "elifkara",
            "name": "Elif Kara",
            "avatar": "https://i.pravatar.cc/80?img=47",
        },
        "type": "review",
        "content": {
            "id": "book-203",
            "title": "Tomorrow, and Tomorrow, and Tomorrow",
            "year": 2022,
            "poster": "https://covers.openlibrary.org/b/id/13214731-L.jpg",
            "kind": "book",
        },
        "score": 8,
        "comment": "Arkadaşlık, oyun tasarımı ve hayatın anlamı üzerine dokunaklı bir hikaye.",
        "timestamp": "1 hafta önce",
        "likes": 19,
        "comments": 7,
    },
    {
        "id": "act-011",
        "user": {
            "username": "ozgurbakir",
            "name": "Özgür Bakır",
            "avatar": "https://i.pravatar.cc/80?img=52",
        },
        "type": "rating",
        "content": {
            "id": "mov-103",
            "title": "Barbie",
            "year": 2023,
            "poster": "https://image.tmdb.org/t/p/w500/cImwv69n5s86vQZBdY3KFf1JQVE.jpg",
            "kind": "film",
        },
        "score": 7,
        "comment": None,
        "timestamp": "2 hafta önce",
        "likes": 22,
        "comments": 9,
    },
    {
        "id": "act-012",
        "user": {
            "username": "selinay",
            "name": "Selin Aydın",
            "avatar": "https://i.pravatar.cc/80?img=15",
        },
        "type": "review",
        "content": {
            "id": "book-204",
            "title": "The Midnight Library",
            "year": 2020,
            "poster": "https://covers.openlibrary.org/b/id/10532476-L.jpg",
            "kind": "book",
        },
        "score": 8,
        "comment": "Hayatımızdaki seçimlerin değeri üzerine duygusal ve düşündürücü bir roman.",
        "timestamp": "2 hafta önce",
        "likes": 17,
        "comments": 6,
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

