from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from flask import Flask, redirect, render_template, request, url_for

from data.sample_data import (
    FEED_ACTIVITIES,
    FEATURED_LISTS,
    FEATURED_USERS,
    LIBRARY_TABS,
    POPULAR_CONTENT,
    USER_PROFILES,
)


app = Flask(__name__)


@dataclass
class ContentItem:
    content_id: str
    title: str
    kind: str
    poster: str
    year: Optional[int] = None
    score: Optional[float] = None


def build_content_index() -> Dict[str, ContentItem]:
    items: Dict[str, ContentItem] = {}

    def _register(payload: Dict[str, Any]) -> None:
        content_id = payload["id"]
        items[content_id] = ContentItem(
            content_id=content_id,
            title=payload["title"],
            kind=payload.get("kind", "film"),
            poster=payload.get("poster", ""),
            year=payload.get("year"),
            score=payload.get("score"),
        )

    for activity in FEED_ACTIVITIES:
        content = activity.get("content")
        if content:
            _register(content)

    for section in POPULAR_CONTENT.values():
        for item in section:
            _register(item)

    return items


CONTENT_INDEX = build_content_index()


@app.context_processor
def inject_globals():
    return {
        "featured_users": FEATURED_USERS,
        "platform_title": "Sosyal Kütüphane",
    }


@app.route("/")
def feed():
    page = int(request.args.get("page", 1))
    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    paginated = FEED_ACTIVITIES[start:end]
    has_more = end < len(FEED_ACTIVITIES)
    return render_template(
        "feed.html",
        activities=paginated,
        featured_lists=FEATURED_LISTS,
        current_page=page,
        has_more=has_more,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        # Placeholder authentication logic for prototype
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        if not email or not password:
            error = "Lütfen e-posta ve şifre alanlarını doldurun."
        else:
            return redirect(url_for("feed"))
    return render_template("auth/login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        required_fields = ["username", "email", "password", "confirm_password"]
        missing = [field for field in required_fields if not request.form.get(field)]
        if missing:
            error = "Lütfen formdaki tüm alanları doldurun."
        elif request.form.get("password") != request.form.get("confirm_password"):
            error = "Şifreler uyuşmuyor."
        else:
            return redirect(url_for("login"))
    return render_template("auth/register.html", error=error)


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    message = None
    if request.method == "POST":
        email = request.form.get("email")
        if email:
            message = "Eğer hesabınız varsa sıfırlama bağlantısı e-posta adresinize gönderildi."
    return render_template("auth/forgot_password.html", message=message)


@app.route("/explore")
def explore():
    query = request.args.get("q", "").strip()
    min_score = request.args.get("min_score")

    filtered_sections = defaultdict(list)
    for section_name, items in POPULAR_CONTENT.items():
        for item in items:
            if query and query.lower() not in item["title"].lower():
                continue
            if min_score and item.get("score") and item["score"] < float(min_score):
                continue
            filtered_sections[section_name].append(item)

    return render_template(
        "explore.html",
        sections=filtered_sections or POPULAR_CONTENT,
        query=query,
        min_score=min_score or "",
    )


@app.route("/content/<content_type>/<content_id>")
def content_detail(content_type: str, content_id: str):
    content = CONTENT_INDEX.get(content_id)
    if not content:
        return render_template("content_detail.html", content=None), 404

    sample_comments = [
        {
            "user": "elifkara",
            "avatar": "https://i.pravatar.cc/60?img=47",
            "text": "Görsel anlatımı nefes kesiciydi, özellikle final sekansı.",
            "timestamp": "2 gün önce",
        },
        {
            "user": "selinay",
            "avatar": "https://i.pravatar.cc/60?img=15",
            "text": "Karakter gelişimi biraz zayıf kalsa da dünya inşası harika.",
            "timestamp": "5 gün önce",
        },
    ]

    return render_template(
        "content_detail.html",
        content=content,
        comments=sample_comments,
    )


@app.route("/profile/<username>")
def profile(username: str):
    profile_data = USER_PROFILES.get(username)
    if not profile_data:
        return render_template("profile.html", profile=None), 404

    return render_template(
        "profile.html",
        profile=profile_data,
        library_tabs=LIBRARY_TABS,
        featured_lists=FEATURED_LISTS,
        activities=FEED_ACTIVITIES[:5],
    )


if __name__ == "__main__":
    app.run(debug=True)

