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

