"""Helpers for populating the development DB using sample_data.

This module provides a conservative seeding routine used only in DEBUG
mode when the database has no users. It's intended to give the UI realistic
data backed by the models during development. Production should rely on
external API ingestion and migrations instead.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict

from backend.extensions import db
from backend.models import (
    User,
    Content,
    Activity,
    LibraryItem,
    CustomList,
    Rating,
    Review,
)
from backend.clients import search_tmdb_movies, search_google_books
import os
import random
from datetime import datetime
from data.sample_data import FEED_ACTIVITIES, POPULAR_CONTENT, FEATURED_USERS, USER_PROFILES, LIBRARY_TABS


def _ensure_user(u: Dict):
    existing = User.query.filter_by(username=u.get("username")).first()
    if existing:
        return existing
    user = User(
        username=u.get("username"),
        email=u.get("email", f"{u.get('username')}@example.dev"),
        password_hash="seeded",  # not used for dev logins
        display_name=u.get("name") or u.get("username"),
        avatar_url=u.get("avatar"),
        bio=(u.get("bio") if u.get("bio") else None),
    )
    db.session.add(user)
    db.session.flush()  # get id
    return user


def _ensure_content(item: Dict):
    # Attempt to match by title + kind
    title = item.get("title")
    kind = item.get("kind")
    content_type = "movie" if kind == "film" else "book"
    existing = (
        Content.query.filter_by(title=title, content_type=content_type).first()
    )
    if existing:
        return existing
    c = Content(
        external_id=item.get("id"),
        content_type=content_type,
        title=title,
        synopsis=item.get("synopsis"),
        release_year=item.get("year"),
        cover_url=item.get("poster") or item.get("cover"),
    )
    db.session.add(c)
    db.session.flush()
    return c


def seed_from_sample_data():
    """Populate DB with a small initial dataset derived from sample_data.

    Safe to run multiple times in development; checks for existing users to
    avoid duplication.
    """
    # create some users first
    users = []
    for u in FEATURED_USERS:
        obj = {
            "username": u["username"],
            "name": u.get("name"),
            "avatar": None,
            "email": f"{u['username']}@example.dev",
        }
        users.append(_ensure_user(obj))

    # add users found in USER_PROFILES too (to get bio/avatars)
    for username, data in USER_PROFILES.items():
        user_obj = {**data, "username": username}
        users.append(_ensure_user(user_obj))

    # Create contents and activities from FEED_ACTIVITIES
    for a in FEED_ACTIVITIES:
        content = _ensure_content(a["content"]) if a.get("content") else None
        # pick or create a user
        udata = a.get("user", {})
        user = _ensure_user({"username": udata.get("username"), "name": udata.get("name"), "avatar": udata.get("avatar")})

        # Check if this activity already exists
        existing_act = Activity.query.filter_by(
            user_id=user.id,
            activity_type=a.get("type"),
            related_id=(content.id if content else None)
        ).first()
        
        if not existing_act:
            act = Activity(
                user_id=user.id,
                activity_type=a.get("type"),
                related_id=(content.id if content else None),
                extra_metadata={"score": a.get("score"), "comment": a.get("comment"), "likes": a.get("likes", 0), "comments": a.get("comments", 0)},
                created_at=datetime.utcnow(),
            )
            db.session.add(act)
        
        # Also create corresponding Rating or Review records where applicable
        if a.get("type") == "rating" and a.get("score") and content:
            # add a rating if not already present
            existing_r = Rating.query.filter_by(user_id=user.id, content_id=content.id).first()
            if not existing_r:
                r = Rating(user_id=user.id, content_id=content.id, score=int(a.get("score")))
                db.session.add(r)
        if a.get("type") == "review" and a.get("comment") and content:
            existing_rev = Review.query.filter_by(user_id=user.id, content_id=content.id).first()
            if not existing_rev:
                rev = Review(user_id=user.id, content_id=content.id, body=a.get("comment"))
                db.session.add(rev)

    # Populate some library entries from LIBRARY_TABS for first user if present
    if users:
        owner = users[0]
        for status, items in LIBRARY_TABS.items():
            for it in items[:2]:
                content = _ensure_content({"title": it.get("title"), "year": it.get("year"), "poster": it.get("poster"), "kind": "film"})
                li = LibraryItem(user_id=owner.id, content_id=content.id, status=status)
                db.session.add(li)

    db.session.commit()

    # Optionally seed some popular external content into the feed
    try:
        if os.getenv("SEED_POPULAR_EXTERNAL", "false").lower() == "true":
            _seed_popular_external_into_feed(users)
    except Exception:
        # don't fail seeding if external clients are unavailable
        pass


def _seed_popular_external_into_feed(existing_users, limit: int = 10):
    """Optional development helper: fetch popular movies/books and create
    Content + Rating + Activity entries so feed shows lively external items.

    Controlled by env `SEED_POPULAR_EXTERNAL=true` to avoid network calls by default.
    """
    if not existing_users:
        return
    owner = existing_users[0]
    # broad queries to surface a variety of results; these functions are resilient
    # and will no-op if requests/key missing.
    movie_results = search_tmdb_movies("the", limit=limit) or []
    book_results = search_google_books("the", limit=limit) or []
    created = 0
    for r in (movie_results + book_results):
        if not r:
            continue
        ext_id = r.get("external_id") or r.get("id")
        if not ext_id:
            continue
        # skip if already ingested
        if Content.query.filter_by(external_id=ext_id).first():
            continue
        try:
            cont = Content(
                external_id=ext_id,
                content_type=("movie" if r.get("kind") == "film" else "book"),
                title=r.get("title") or "Untitled",
                release_year=int(r.get("year")) if r.get("year") else None,
                cover_url=r.get("poster") or None,
                runtime_minutes=r.get("runtime_minutes"),
                page_count=r.get("page_count"),
                extra_metadata=r.get("extra") or r.get("extra_details") or {},
            )
            db.session.add(cont)
            db.session.flush()

            # add a faux rating so feed shows a rating activity
            score = random.randint(7, 9)
            rating = Rating(user_id=owner.id, content_id=cont.id, score=score)
            db.session.add(rating)

            act = Activity(user_id=owner.id, activity_type="rating", related_id=cont.id, extra_metadata={"score": score}, created_at=datetime.utcnow())
            db.session.add(act)

            created += 1
            if created >= limit:
                break
        except Exception:
            # ignore individual failures
            continue
    if created:
        db.session.commit()


def seed_activities_from_existing() -> int:
    """Create Activity rows for existing Rating and Review records where missing.

    Returns the number of Activity rows created.
    """
    created = 0
    # Ratings -> rating activities
    for r in Rating.query.all():
        try:
            exists = Activity.query.filter_by(user_id=r.user_id, activity_type="rating", related_id=r.content_id).first()
            if exists:
                continue
            act = Activity(
                user_id=r.user_id,
                activity_type="rating",
                related_id=r.content_id,
                extra_metadata={"score": r.score},
                created_at=(r.created_at if hasattr(r, 'created_at') and r.created_at else datetime.utcnow()),
            )
            db.session.add(act)
            created += 1
        except Exception:
            continue

    # Reviews -> review activities
    for rev in Review.query.all():
        try:
            exists = Activity.query.filter_by(user_id=rev.user_id, activity_type="review", related_id=rev.content_id).first()
            if exists:
                continue
            act = Activity(
                user_id=rev.user_id,
                activity_type="review",
                related_id=rev.content_id,
                extra_metadata={"comment": rev.body},
                created_at=(rev.created_at if hasattr(rev, 'created_at') and rev.created_at else datetime.utcnow()),
            )
            db.session.add(act)
            created += 1
        except Exception:
            continue

    if created:
        db.session.commit()
    return created

