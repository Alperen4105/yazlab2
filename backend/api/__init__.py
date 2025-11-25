from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from sqlalchemy import or_

from backend.extensions import db
from backend.models import User
from backend.security import hash_password, verify_password
from data.sample_data import (
    FEED_ACTIVITIES,
    FEATURED_LISTS,
    FEATURED_USERS,
    LIBRARY_TABS,
    POPULAR_CONTENT,
    USER_PROFILES,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _paginate(items, page: int, per_page: int):
    start = (page - 1) * per_page
    end = start + per_page
    slice_ = items[start:end]
    return {
        "items": slice_,
        "page": page,
        "per_page": per_page,
        "has_more": end < len(items),
        "total": len(items),
    }


@api_bp.get("/feed")
def api_feed():
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 10)), 25)
    payload = _paginate(FEED_ACTIVITIES, page, per_page)
    payload["featured_lists"] = FEATURED_LISTS
    payload["featured_users"] = FEATURED_USERS
    return jsonify(payload)


@api_bp.get("/explore")
def api_explore():
    query = request.args.get("q", "").lower()
    min_score = request.args.get("min_score")

    results = []
    sections = {}
    for section_name, section_items in POPULAR_CONTENT.items():
        filtered = []
        for item in section_items:
            if query and query not in item["title"].lower():
                continue
            if min_score and item.get("score") and item["score"] < float(min_score):
                continue
            filtered.append(item)
            results.append(item)
        if filtered:
            sections[section_name] = filtered

    if not sections:
        sections = POPULAR_CONTENT
        results = [item for items in POPULAR_CONTENT.values() for item in items]

    return jsonify(
        {"items": results, "sections": sections, "query": query, "count": len(results)}
    )


@api_bp.get("/content/<content_id>")
def api_content_detail(content_id: str):
    all_items = []
    for collection in POPULAR_CONTENT.values():
        all_items.extend(collection)
    for activity in FEED_ACTIVITIES:
        if activity.get("content"):
            all_items.append(activity["content"])

    content = next((item for item in all_items if item["id"] == content_id), None)
    if not content:
        return jsonify({"message": "Content not found"}), 404

    comments = [
        {
            "user": "elifkara",
            "text": "Ön plana çıkan atmosferi çok sevdim.",
            "timestamp": "2 gün önce",
        },
        {
            "user": "selinay",
            "text": "Karakterler daha derin olabilirdi ama genel olarak iyiydi.",
            "timestamp": "5 gün önce",
        },
    ]

    return jsonify({"content": content, "comments": comments})


@api_bp.get("/profiles/<username>")
def api_profile(username: str):
    user = USER_PROFILES.get(username)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(
        {
            "profile": user,
            "library": LIBRARY_TABS,
            "featured_lists": FEATURED_LISTS,
            "recent_activities": FEED_ACTIVITIES[:5],
        }
    )


@api_bp.post("/auth/login")
def api_login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"message": "Email ve şifre gerekli."}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(user.password_hash, password):
        return jsonify({"message": "E-posta veya şifre hatalı."}), 401

    tokens = {
        "access_token": create_access_token(identity=user.id),
        "refresh_token": create_refresh_token(identity=user.id),
    }
    return jsonify({**tokens, "user": user.to_dict()})


@api_bp.post("/auth/register")
def api_register():
    data = request.get_json() or {}
    required = ("username", "email", "password")
    missing = [field for field in required if not data.get(field)]
    if missing:
        return jsonify({"message": f"Eksik alanlar: {', '.join(missing)}"}), 400

    existing = User.query.filter(
        or_(User.username == data["username"], User.email == data["email"])
    ).first()
    if existing:
        return jsonify({"message": "Kullanıcı adı veya e-posta zaten kullanımda."}), 409

    user = User(
        username=data["username"],
        email=data["email"],
        password_hash=hash_password(data["password"]),
        display_name=data.get("display_name") or data["username"],
    )
    db.session.add(user)
    db.session.commit()

    tokens = {
        "access_token": create_access_token(identity=user.id),
        "refresh_token": create_refresh_token(identity=user.id),
    }
    return jsonify({**tokens, "user": user.to_dict()}), 201


@api_bp.post("/auth/refresh")
@jwt_required(refresh=True)
def api_refresh():
    identity = get_jwt_identity()
    return jsonify({"access_token": create_access_token(identity=identity)})

