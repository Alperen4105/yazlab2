from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    verify_jwt_in_request,
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
from backend.models import Activity, Content, LibraryItem, Rating, Review, ReviewReaction, CustomList, CustomListItem, Follow
from backend.clients import (
    search_tmdb_movies,
    search_google_books,
    get_tmdb_movie_details,
    get_book_details,
)
from datetime import timezone
import os

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _paginate(items, page: int, per_page: int):
    start = (page - 1) * per_page
    end = start + per_page
    slice_ = items[start:end]
    return {
        "items": slice_,
        "page": page,
        "has_more": end < len(items),
        "total": len(items),
    }



@api_bp.get("/feed")
def api_feed():
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 10)), 25)
    # Try to use DB-backed activities first; fallback to sample data when empty
    items = []
    # If caller is authenticated and follows people, show followed users' activities
    follower_identity = None
    try:
        # Accept both missing token and token-based identity
        follower_identity = get_jwt_identity()
        if follower_identity is not None:
            try:
                follower_identity = int(follower_identity)
            except Exception:
                pass
    except Exception:
        follower_identity = None

    if follower_identity:
        followed_ids = [f.followed_id for f in Follow.query.filter_by(follower_id=follower_identity).all()]
        if followed_ids:
            q = Activity.query.filter(Activity.user_id.in_(followed_ids)).order_by(Activity.created_at.desc())
        else:
            q = Activity.query.order_by(Activity.created_at.desc())
    else:
        q = Activity.query.order_by(Activity.created_at.desc())
    total = q.count()
    start = (page - 1) * per_page
    db_items = q.offset(start).limit(per_page).all()
    for a in db_items:
        user = a.user
        content = None
        if a.related_id:
            content = Content.query.get(a.related_id)

        item = {
            "id": f"act-{a.id}",
            "user": {
                "username": user.username,
                "name": user.display_name or user.username,
                "avatar": user.avatar_url,
            },
            "type": a.activity_type,
            "content": None,
            "score": None,
            "comment": None,
            "timestamp": a.created_at.isoformat() if a.created_at else None,
            "likes": a.extra_metadata.get("likes") if a.extra_metadata else 0,
            "comments": a.extra_metadata.get("comments") if a.extra_metadata else 0,
        }
        if content:
            item["content"] = {
                "id": f"content-{content.id}",
                "title": content.title,
                "year": content.release_year,
                "poster": content.cover_url,
                "kind": "film" if content.content_type == "movie" else "book",
            }
            if a.extra_metadata:
                item["score"] = a.extra_metadata.get("score")
                item["comment"] = a.extra_metadata.get("comment")
        items.append(item)

    payload = {
        "items": items,
        "page": page,
        "per_page": per_page,
        "has_more": (start + len(items)) < total,
        "total": total,
    }
    # If DB is empty fallback to sample data
    if total == 0:
        payload = _paginate(FEED_ACTIVITIES, page, per_page)
    payload["featured_lists"] = FEATURED_LISTS
    payload["featured_users"] = FEATURED_USERS
    return jsonify(payload)


@api_bp.get("/explore")
def api_explore():
    query = request.args.get("q", "").lower()
    results = []
    sections = {}

    # Prefer DB content; fallback to POPULAR_CONTENT when DB empty
    db_count = Content.query.count()
    if db_count:
        # Fetch all contents and filter in Python (sufficient for small dev DB)
        all_contents = Content.query.all()
        for c in all_contents:
            title = (c.title or "").lower()
            if query and query not in title:
                continue
            # compute average score from ratings
            avg = None
            if hasattr(c, "ratings"):
                scores = [r.score for r in c.ratings]
                if scores:
                    avg = sum(scores) / len(scores)

            item = {
                "id": f"content-{c.id}",
                "title": c.title,
                "poster": c.cover_url,
                "score": round(avg, 1) if avg is not None else None,
                "kind": "film" if c.content_type == "movie" else "book",
                "persisted": True,
                "source": "local",
            }
            results.append(item)

        # if the DB returned results, split by type
        if results:
            films = [r for r in results if r["kind"] == "film"]
            books = [r for r in results if r["kind"] == "book"]
            sections = {}
            if films:
                sections["Filmler"] = films
            if books:
                sections["Kitaplar"] = books
            return jsonify({"items": results, "sections": sections, "query": query, "count": len(results)})

        # if the DB returned nothing for the query, try external search
        # When a user explicitly searches and we don't have matching local results
        # reach out to external sources (TMDb / Google Books) and ingest matches.
        if query and not results:
            # try TMDb for movies and Google/OpenLibrary for books
                movie_results = search_tmdb_movies(query, limit=10)
                book_results = search_google_books(query, limit=10)
                results_from_external = movie_results + book_results
                out = []
                ingest_enabled = os.getenv("INGEST_EXTERNAL_RESULTS", "false").lower() == "true"
                for r in results_from_external:
                    if ingest_enabled:
                        # ingest to DB if opt-in requested
                        if Content.query.filter_by(external_id=r.get("external_id")).first():
                            continue
                        cont = Content(
                            external_id=r.get("external_id"),
                            content_type=("movie" if r.get("kind") == "film" else "book"),
                            title=r.get("title") or "Untitled",
                            release_year=int(r.get("year")) if r.get("year") else None,
                            cover_url=r.get("poster") or None,
                            runtime_minutes=r.get("runtime_minutes"),
                            page_count=r.get("page_count"),
                            extra_metadata=r.get("extra"),
                        )
                        db.session.add(cont)
                        db.session.flush()
                        out.append({
                            "id": f"content-{cont.id}",
                            "title": cont.title,
                            "poster": cont.cover_url,
                            "year": cont.release_year,
                            "kind": "film" if cont.content_type == "movie" else "book",
                            "persisted": True,
                            "source": ("tmdb" if (r.get("external_id") or "").startswith("mov-") else "books"),
                        })
                    else:
                        # do not persist search results in DB by default; return mapped items
                        out.append({
                            "id": r.get("id") or r.get("external_id"),
                            "title": r.get("title"),
                            "poster": r.get("poster"),
                            "year": int(r.get("year")) if r.get("year") else None,
                            "kind": "film" if r.get("kind") == "film" else "book",
                            "persisted": False,
                            "source": ("tmdb" if (r.get("external_id") or "").startswith("mov-") else ("openlibrary" if (r.get("external_id") or "").startswith("/") else "google_books")),
                            "runtime_minutes": r.get("runtime_minutes"),
                            "page_count": r.get("page_count"),
                        })
                if ingest_enabled:
                    db.session.commit()
                if out:
                    films = [r for r in out if r["kind"] == "film"]
                    books = [r for r in out if r["kind"] == "book"]
                    sections = {}
                    if films:
                        sections["Filmler"] = films
                    if books:
                        sections["Kitaplar"] = books
                    return jsonify({"items": out, "sections": sections, "query": query, "count": len(out)})

    # fallback
    # If DB is small (or empty) and caller provided a query, try external search/ingest
    if query and not results:
        movie_results = search_tmdb_movies(query, limit=10)
        book_results = search_google_books(query, limit=10)
        results_from_external = movie_results + book_results
        out = []
        ingest_enabled = os.getenv("INGEST_EXTERNAL_RESULTS", "false").lower() == "true"
        for r in results_from_external:
            if ingest_enabled:
                if Content.query.filter_by(external_id=r.get("external_id")).first():
                    continue
                cont = Content(
                    external_id=r.get("external_id"),
                    content_type=("movie" if r.get("kind") == "film" else "book"),
                    title=r.get("title") or "Untitled",
                    release_year=int(r.get("year")) if r.get("year") else None,
                    cover_url=r.get("poster") or None,
                    runtime_minutes=r.get("runtime_minutes"),
                    page_count=r.get("page_count"),
                    extra_metadata=r.get("extra"),
                )
                db.session.add(cont)
                db.session.flush()
                out.append({
                        "id": f"content-{cont.id}",
                        "title": cont.title,
                        "poster": cont.cover_url,
                        "year": cont.release_year,
                        "kind": "film" if cont.content_type == "movie" else "book",
                        "persisted": True,
                        "source": ("tmdb" if (r.get("external_id") or "").startswith("mov-") else "books"),
                    })
            else:
                out.append({
                        "id": r.get("id") or r.get("external_id"),
                        "title": r.get("title"),
                        "poster": r.get("poster"),
                        "year": int(r.get("year")) if r.get("year") else None,
                        "kind": "film" if r.get("kind") == "film" else "book",
                        "persisted": False,
                        "source": ("tmdb" if (r.get("external_id") or "").startswith("mov-") else ("openlibrary" if (r.get("external_id") or "").startswith("/") else "google_books")),
                        "runtime_minutes": r.get("runtime_minutes"),
                        "page_count": r.get("page_count"),
                    })
        if ingest_enabled:
            db.session.commit()
        if out:
            films = [r for r in out if r["kind"] == "film"]
            books = [r for r in out if r["kind"] == "book"]
            sections = {}
            if films:
                sections["Filmler"] = films
            if books:
                sections["Kitaplar"] = books
            return jsonify({"items": out, "sections": sections, "query": query, "count": len(out)})
    for section_name, section_items in POPULAR_CONTENT.items():
        filtered = []
        for item in section_items:
            if query and query not in item["title"].lower():
                continue
            # clone the sample item and add explicit flags so UI can display source/persisted
            item_copy = dict(item)
            item_copy["persisted"] = False
            item_copy["source"] = "sample"
            filtered.append(item_copy)
            results.append(item_copy)
        if filtered:
            sections[section_name] = filtered

    if not sections:
        sections = POPULAR_CONTENT
        results = [item for items in POPULAR_CONTENT.values() for item in items]

    return jsonify({"items": results, "sections": sections, "query": query, "count": len(results)})


@api_bp.get("/content/<content_id>")
def api_content_detail(content_id: str):
    # Try to get content by external_id first, then numeric id
    # Accept patterns like 'mov-100' (external) or 'content-123' or numeric id
    c = None
    # search by external id
    c = Content.query.filter_by(external_id=content_id).first()
    if not c:
        # try strip common prefix
        if content_id.startswith("content-"):
            try:
                pk = int(content_id.split("content-")[1])
                c = Content.query.get(pk)
            except Exception:
                c = None
        else:
            # maybe numeric id as string
            try:
                pk = int(content_id)
                c = Content.query.get(pk)
            except Exception:
                c = None

    if not c:
        # fallback to sample data
        all_items = []
        for collection in POPULAR_CONTENT.values():
            all_items.extend(collection)
        content = next((item for item in all_items if item["id"] == content_id), None)
        if not content:
                # try live external fetching for external ids (mov-..., book-...)
                if content_id.startswith("mov-"):
                    # ask clients for TMDb details
                    ext = get_tmdb_movie_details(content_id)
                    if ext:
                        cont = {
                            "id": ext.get("id"),
                            "title": ext.get("title"),
                            "year": ext.get("year"),
                            "poster": ext.get("poster"),
                            "kind": "film",
                            "platform_score": None,
                            "total_votes": 0,
                            "meta": {"runtime_minutes": ext.get("runtime_minutes")},
                        }
                        return jsonify({"content": cont, "comments": []})
                if content_id.startswith("book-"):
                    ext = get_book_details(content_id)
                    if ext:
                        cont = {
                            "id": ext.get("id"),
                            "title": ext.get("title"),
                            "year": ext.get("year"),
                            "poster": ext.get("poster"),
                            "kind": "book",
                            "platform_score": None,
                            "total_votes": 0,
                            "meta": {"page_count": ext.get("page_count")},
                        }
                        return jsonify({"content": cont, "comments": []})
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

    # Build content payload from DB record
    # platform score: average of rating scores
    scores = [r.score for r in c.ratings]
    avg = round(sum(scores) / len(scores), 1) if scores else None
    total_votes = len(scores)

    # collect reviews
    comments = []
    # optional: check caller for whether they reacted to reviews
    caller = None
    try:
        verify_jwt_in_request(optional=True)
        caller = get_jwt_identity()
        try:
            caller = int(caller)
        except Exception:
            pass
    except Exception:
        caller = None

    for rev in c.reviews:
        reactions = {"like": 0, "dislike": 0}
        for r in rev.reactions:
            if r.reaction_type == 'like':
                reactions['like'] += 1
            else:
                reactions['dislike'] += 1

        comments.append(
            {
                "id": rev.id,
                "user": rev.user.username,
                "user_id": rev.user_id,
                "avatar": rev.user.avatar_url,
                "text": rev.body,
                "timestamp": rev.created_at.isoformat() if rev.created_at else None,
                "reactions": reactions,
                "current_user_reaction": bool(
                    any(r.user_id == caller for r in rev.reactions) if caller else False
                ),
            }
        )

    content = {
        "id": f"content-{c.id}",
        "title": c.title,
        "year": c.release_year,
        "poster": c.cover_url,
        "kind": "film" if c.content_type == "movie" else "book",
        "platform_score": avg,
        "total_votes": total_votes,
        "meta": {
            "runtime_minutes": c.runtime_minutes,
            "page_count": c.page_count,
        },
    }

    return jsonify({"content": content, "comments": comments})


@api_bp.post("/content/<content_id>/ratings")
@jwt_required()
def api_create_or_update_rating(content_id: str):
    data = request.get_json() or {}
    score = data.get("score")
    if score is None:
        return jsonify({"message": "score required"}), 400
    try:
        score = int(score)
    except Exception:
        return jsonify({"message": "score must be an integer"}), 400
    if score < 1 or score > 10:
        return jsonify({"message": "score must be between 1 and 10"}), 400

    identity = get_jwt_identity()
    try:
        identity = int(identity)
    except Exception:
        pass
    user = User.query.get(identity)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # locate content
    content = Content.query.filter_by(external_id=content_id).first() or (Content.query.get(int(content_id.split('content-')[-1])) if content_id.startswith('content-') else None)
    if not content:
        return jsonify({"message": "Content not found"}), 404

    rating = Rating.query.filter_by(user_id=user.id, content_id=content.id).first()
    if rating:
        rating.score = score
        db.session.commit()
        return jsonify({"message": "rating updated", "rating": {"id": rating.id, "score": rating.score}})

    rating = Rating(user_id=user.id, content_id=content.id, score=score)
    db.session.add(rating)
    db.session.commit()

    # create an activity for the rating
    act = Activity(user_id=user.id, activity_type="rating", related_id=content.id, extra_metadata={"score": score}, created_at=db.func.now())
    db.session.add(act)
    db.session.commit()

    return jsonify({"message": "rating created", "rating": {"id": rating.id, "score": rating.score}}), 201


@api_bp.post("/content/<content_id>/reviews")
@jwt_required()
def api_create_review(content_id: str):
    data = request.get_json() or {}
    body = (data.get("body") or "").strip()
    if not body:
        return jsonify({"message": "body required"}), 400

    identity = get_jwt_identity()
    try:
        identity = int(identity)
    except Exception:
        pass
    user = User.query.get(identity)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # locate content
    content = Content.query.filter_by(external_id=content_id).first() or (Content.query.get(int(content_id.split('content-')[-1])) if content_id.startswith('content-') else None)
    if not content:
        return jsonify({"message": "Content not found"}), 404

    # create review
    review = Review(user_id=user.id, content_id=content.id, body=body)
    db.session.add(review)
    db.session.commit()

    # create activity for review
    act = Activity(user_id=user.id, activity_type="review", related_id=content.id, extra_metadata={"comment": body}, created_at=db.func.now())
    db.session.add(act)
    db.session.commit()

    return jsonify({"message": "review created", "review": {"id": review.id, "body": review.body}}), 201


@api_bp.put("/reviews/<int:review_id>")
@jwt_required()
def api_update_review(review_id: int):
    data = request.get_json() or {}
    body = (data.get("body") or "").strip()
    if not body:
        return jsonify({"message": "body required"}), 400

    identity = get_jwt_identity()
    try:
        identity = int(identity)
    except Exception:
        pass
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"message": "review not found"}), 404
    if review.user_id != identity:
        return jsonify({"message": "forbidden"}), 403

    review.body = body
    db.session.commit()
    return jsonify({"message": "review updated", "review": {"id": review.id, "body": review.body}})


@api_bp.delete("/reviews/<int:review_id>")
@jwt_required()
def api_delete_review(review_id: int):
    identity = get_jwt_identity()
    try:
        identity = int(identity)
    except Exception:
        pass
    review = Review.query.get(review_id)
    if not review:
        return jsonify({"message": "review not found"}), 404
    if review.user_id != identity:
        return jsonify({"message": "forbidden"}), 403

    # delete related activity if exists
    Activity.query.filter_by(user_id=identity, activity_type="review", related_id=review.content_id).delete()
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "review deleted"})


@api_bp.post("/activities/<int:activity_id>/like")
@jwt_required()
def api_like_activity(activity_id: int):
    # increment likes counter in Activity.extra_metadata (simple implementation)
    a = Activity.query.get(activity_id)
    if not a:
        return jsonify({"message": "Activity not found"}), 404
    meta = a.extra_metadata or {}
    likes = meta.get("likes") or 0
    likes += 1
    meta["likes"] = likes
    a.extra_metadata = meta
    db.session.commit()
    return jsonify({"message": "liked", "likes": likes})


@api_bp.post("/reviews/<int:review_id>/reactions")
@jwt_required()
def api_add_review_reaction(review_id: int):
    data = request.get_json() or {}
    reaction_type = data.get("reaction_type")
    if reaction_type not in ("like", "dislike"):
        return jsonify({"message": "reaction_type must be 'like' or 'dislike'"}), 400

    identity = get_jwt_identity()
    try:
        identity = int(identity)
    except Exception:
        pass

    review = Review.query.get(review_id)
    if not review:
        return jsonify({"message": "review not found"}), 404

    exists = ReviewReaction.query.filter_by(review_id=review_id, user_id=identity).first()
    if exists:
        return jsonify({"message": "already reacted"}), 409

    rr = ReviewReaction(review_id=review_id, user_id=identity, reaction_type=reaction_type)
    db.session.add(rr)
    db.session.commit()
    return jsonify({"message": "reacted", "reaction": {"id": rr.id, "type": rr.reaction_type}}), 201


@api_bp.delete("/reviews/<int:review_id>/reactions")
@jwt_required()
def api_remove_review_reaction(review_id: int):
    identity = get_jwt_identity()
    try:
        identity = int(identity)
    except Exception:
        pass
    rr = ReviewReaction.query.filter_by(review_id=review_id, user_id=identity).first()
    if not rr:
        return jsonify({"message": "reaction not found"}), 404
    db.session.delete(rr)
    db.session.commit()
    return jsonify({"message": "reaction removed"})


@api_bp.post("/content/<content_id>/library")
@jwt_required()
def api_add_library_item(content_id: str):
    data = request.get_json() or {}
    status = data.get("status")
    if not status:
        return jsonify({"message": "status required"}), 400

    identity = get_jwt_identity()
    try:
        identity = int(identity)
    except Exception:
        pass

    user = User.query.get(identity)
    if not user:
        return jsonify({"message": "User not found"}), 404

    content = Content.query.filter_by(external_id=content_id).first() or (Content.query.get(int(content_id.split('content-')[-1])) if content_id.startswith('content-') else None)
    if not content:
        return jsonify({"message": "Content not found"}), 404

    existing = LibraryItem.query.filter_by(user_id=user.id, content_id=content.id).first()
    if existing:
        return jsonify({"message": "already exists"}), 409

    li = LibraryItem(user_id=user.id, content_id=content.id, status=status)
    db.session.add(li)
    db.session.commit()
    return jsonify({"message": "added", "item": {"id": li.id, "status": li.status}}), 201


@api_bp.delete("/content/<content_id>/library")
@jwt_required()
def api_remove_library_item(content_id: str):
    identity = get_jwt_identity()
    try:
        identity = int(identity)
    except Exception:
        pass
    user = User.query.get(identity)
    if not user:
        return jsonify({"message": "User not found"}), 404

    content = Content.query.filter_by(external_id=content_id).first() or (Content.query.get(int(content_id.split('content-')[-1])) if content_id.startswith('content-') else None)
    if not content:
        return jsonify({"message": "Content not found"}), 404

    existing = LibraryItem.query.filter_by(user_id=user.id, content_id=content.id).first()
    if not existing:
        return jsonify({"message": "not found"}), 404

    db.session.delete(existing)
    db.session.commit()
    return jsonify({"message": "removed"})


@api_bp.post("/lists")
@jwt_required()
def api_create_list():
    data = request.get_json() or {}
    title = data.get("title")
    if not title:
        return jsonify({"message": "title required"}), 400
    description = data.get("description")
    visibility = data.get("visibility") or "public"

    identity = get_jwt_identity()
    try:
        identity = int(identity)
    except Exception:
        pass
    user = User.query.get(identity)
    if not user:
        return jsonify({"message": "User not found"}), 404

    lst = CustomList(user_id=user.id, title=title, description=description, visibility=visibility)
    db.session.add(lst)
    db.session.commit()
    return jsonify({"id": lst.id, "title": lst.title}), 201


@api_bp.post("/lists/<int:list_id>/items")
@jwt_required()
def api_add_list_item(list_id: int):
    data = request.get_json() or {}
    content_id = data.get("content_id")
    if not content_id:
        return jsonify({"message": "content_id required"}), 400

    identity = get_jwt_identity()
    try:
        identity = int(identity)
    except Exception:
        pass
    user = User.query.get(identity)
    if not user:
        return jsonify({"message": "User not found"}), 404

    lst = CustomList.query.get(list_id)
    if not lst:
        return jsonify({"message": "list not found"}), 404
    if lst.user_id != user.id:
        return jsonify({"message": "forbidden"}), 403

    content = Content.query.filter_by(external_id=content_id).first() or (Content.query.get(int(content_id.split('content-')[-1])) if content_id.startswith('content-') else None)
    if not content:
        return jsonify({"message": "Content not found"}), 404

    cli = CustomListItem(list_id=lst.id, content_id=content.id)
    db.session.add(cli)
    db.session.commit()
    return jsonify({"id": cli.id, "content_id": content.id}), 201


@api_bp.delete("/lists/<int:list_id>")
@jwt_required()
def api_delete_list(list_id: int):
    identity = get_jwt_identity()
    try:
        identity = int(identity)
    except Exception:
        pass
    user = User.query.get(identity)
    if not user:
        return jsonify({"message": "User not found"}), 404

    lst = CustomList.query.get(list_id)
    if not lst:
        return jsonify({"message": "list not found"}), 404
    if lst.user_id != user.id:
        return jsonify({"message": "forbidden"}), 403

    # cascade delete handled by DB relations
    db.session.delete(lst)
    db.session.commit()
    return jsonify({"message": "deleted"})


@api_bp.post('/users/<username>/follow')
@jwt_required()
def api_follow_user(username: str):
    identity = get_jwt_identity()
    try:
        identity = int(identity)
    except Exception:
        pass
    follower = User.query.get(identity)
    if not follower:
        return jsonify({'message': 'User not found'}), 404

    target = User.query.filter_by(username=username).first()
    if not target:
        return jsonify({'message': 'target not found'}), 404
    if follower.id == target.id:
        return jsonify({'message': 'cannot follow yourself'}), 400

    exists = Follow.query.filter_by(follower_id=follower.id, followed_id=target.id).first()
    if exists:
        return jsonify({'message': 'already following'}), 409

    f = Follow(follower_id=follower.id, followed_id=target.id)
    db.session.add(f)
    db.session.commit()
    return jsonify({'message': 'followed'}), 201


@api_bp.delete('/users/<username>/follow')
@jwt_required()
def api_unfollow_user(username: str):
    identity = get_jwt_identity()
    try:
        identity = int(identity)
    except Exception:
        pass
    follower = User.query.get(identity)
    if not follower:
        return jsonify({'message': 'User not found'}), 404

    target = User.query.filter_by(username=username).first()
    if not target:
        return jsonify({'message': 'target not found'}), 404

    exists = Follow.query.filter_by(follower_id=follower.id, followed_id=target.id).first()
    if not exists:
        return jsonify({'message': 'not following'}), 404

    db.session.delete(exists)
    db.session.commit()
    return jsonify({'message': 'unfollowed'})


@api_bp.get("/profiles/<username>")
def api_profile(username: str):
    # Try to load the profile from DB; fallback to sample data
    user_obj = User.query.filter_by(username=username).first()
    if not user_obj:
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

    # Build library sections
    library_entries = LibraryItem.query.filter_by(user_id=user_obj.id).all()
    tabs = {"watched": [], "watchlist": [], "read": [], "reading_list": []}
    for li in library_entries:
        tabs.setdefault(li.status, []).append(
            {"title": li.content.title, "year": li.content.release_year, "poster": li.content.cover_url}
        )

    # recent activities
    recent = (
        Activity.query.filter_by(user_id=user_obj.id)
        .order_by(Activity.created_at.desc())
        .limit(5)
        .all()
    )
    recent_items = []
    for a in recent:
        content = Content.query.get(a.related_id) if a.related_id else None
        # include user meta so templates expecting activity.user.* work
        recent_items.append(
            {
                "type": a.activity_type,
                "user": {
                    "username": user_obj.username,
                    "name": user_obj.display_name or user_obj.username,
                    "avatar": user_obj.avatar_url,
                },
                "content": {
                    "title": content.title if content else None,
                    "poster": content.cover_url if content else None,
                    "id": f"content-{content.id}" if content else None,
                },
                "timestamp": a.created_at.isoformat() if a.created_at else None,
            }
        )

    profile = user_obj.to_dict()
    # ensure template-friendly keys exist
    profile["name"] = profile.get("display_name") or profile.get("username")
    profile["avatar"] = profile.get("avatar_url")
    profile["followers"] = user_obj.followers.count() if hasattr(user_obj, "followers") else 0
    profile["following"] = user_obj.following.count() if hasattr(user_obj, "following") else 0

    # check if the caller follows this user (if a token was provided)
    caller = None
    # Verify token if present (optional) so get_jwt_identity can read it
    try:
        verify_jwt_in_request(optional=True)
        caller = get_jwt_identity()
        if caller is not None:
            try:
                caller = int(caller)
            except Exception:
                pass
    except Exception:
        caller = None

    is_following = False
    if caller:
        is_following = bool(Follow.query.filter_by(follower_id=caller, followed_id=user_obj.id).first())

    return jsonify(
        {
            "profile": profile,
            "library": tabs,
            "featured_lists": FEATURED_LISTS,
            "recent_activities": recent_items,
            "is_following": is_following,
        }
    )


@api_bp.put("/profiles/<username>")
@jwt_required()
def api_update_profile(username: str):
    """Update user profile (bio, display_name, avatar_url)"""
    identity = get_jwt_identity()
    try:
        identity = int(identity)
    except Exception:
        pass
    
    user = User.query.get(identity)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # Verify user is updating their own profile
    if user.username != username:
        return jsonify({"message": "Forbidden"}), 403
    
    data = request.get_json() or {}
    
    # Update allowed fields
    if "bio" in data:
        user.bio = data["bio"]
    if "display_name" in data:
        user.display_name = data["display_name"]
    if "avatar_url" in data:
        user.avatar_url = data["avatar_url"]
        from flask import current_app
        current_app.logger.info(f"Updating avatar for {username}: {data['avatar_url']}")
    
    db.session.commit()
    
    return jsonify({"message": "Profile updated", "user": user.to_dict()})


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
        # store identity as string to avoid token library subject type issues
        "access_token": create_access_token(identity=str(user.id)),
        "refresh_token": create_refresh_token(identity=str(user.id)),
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
        "access_token": create_access_token(identity=str(user.id)),
        "refresh_token": create_refresh_token(identity=str(user.id)),
    }
    return jsonify({**tokens, "user": user.to_dict()}), 201


@api_bp.post("/auth/refresh")
@jwt_required(refresh=True)
def api_refresh():
    identity = get_jwt_identity()
    return jsonify({"access_token": create_access_token(identity=identity)})

