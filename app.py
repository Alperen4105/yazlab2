from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from dotenv import load_dotenv

from backend import init_app
from backend.api.client import call_api

load_dotenv()

app = Flask(__name__, instance_relative_config=True)


def api_request(
    method: str,
    path: str,
    *,
    json: Optional[Dict[str, Any]] = None,
    query_string: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Tuple[Dict[str, Any], int]:
    data, status = call_api(
        method,
        path,
        json=json,
        query_string=query_string,
        headers=headers,
    )
    return data or {}, status


@app.context_processor
def inject_globals():
    auth = session.get("auth", {})
    return {
        "platform_title": "Sosyal Kütüphane",
        "current_user": auth.get("user"),
    }


@app.route("/")
def feed():
    page = int(request.args.get("page", 1))
    data, status = api_request("get", "/api/feed", query_string={"page": page})
    if status != 200:
        abort(status)
    return render_template(
        "feed.html",
        activities=data.get("items", []),
        featured_lists=data.get("featured_lists", []),
        featured_users=data.get("featured_users", []),
        current_page=page,
        has_more=data.get("has_more", False),
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        payload, status = api_request(
            "post",
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        if status == 200:
            session["auth"] = {
                "access_token": payload.get("access_token"),
                "refresh_token": payload.get("refresh_token"),
                "user": payload.get("user"),
            }
            flash("Hoş geldiniz!", "success")
            return redirect(url_for("feed"))
        error = payload.get("message", "Giriş yapılamadı.")
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
            payload, status = api_request(
                "post",
                "/api/auth/register",
                json={
                    "username": request.form["username"],
                    "email": request.form["email"],
                    "password": request.form["password"],
                    "display_name": request.form.get("username"),
                },
            )
            if status == 201:
                session["auth"] = {
                    "access_token": payload.get("access_token"),
                    "refresh_token": payload.get("refresh_token"),
                    "user": payload.get("user"),
                }
                flash("Hesabınız oluşturuldu!", "success")
                return redirect(url_for("feed"))
            error = payload.get("message", "Kayıt sırasında bir hata oluştu.")
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
    payload, status = api_request(
        "get",
        "/api/explore",
        query_string={"q": query, "min_score": min_score},
    )
    if status != 200:
        abort(status)
    return render_template(
        "explore.html",
        sections=payload.get("sections", {}),
        query=query,
        min_score=min_score or "",
    )


@app.route("/content/<content_type>/<content_id>")
def content_detail(content_type: str, content_id: str):
    if request.method == "POST":
        # handle new comment or rating from frontend form
        auth = session.get("auth", {})
        access = auth.get("access_token")
        if not access:
            flash("Lütfen önce giriş yapın.", "warning")
            return redirect(url_for("login"))

        # decide whether it's a rating, review, edit/delete review, reaction, or library action
        # handling edit/delete/reaction for reviews
        if request.form.get("edit_review_id"):
            review_id = request.form.get("edit_review_id")
            body = request.form.get("body")
            payload, status = api_request(
                "put",
                f"/api/reviews/{review_id}",
                json={"body": body},
                headers={"Authorization": f"Bearer {access}"},
            )
        elif request.form.get("delete_review_id"):
            review_id = request.form.get("delete_review_id")
            payload, status = api_request(
                "delete",
                f"/api/reviews/{review_id}",
                headers={"Authorization": f"Bearer {access}"},
            )
        elif request.form.get("react_review_id"):
            rv = request.form.get("react_review_id")
            action = request.form.get("reaction_action")
            rtype = request.form.get("reaction_type")
            if action == "add":
                payload, status = api_request(
                    "post",
                    f"/api/reviews/{rv}/reactions",
                    json={"reaction_type": rtype},
                    headers={"Authorization": f"Bearer {access}"},
                )
            else:
                payload, status = api_request(
                    "delete",
                    f"/api/reviews/{rv}/reactions",
                    headers={"Authorization": f"Bearer {access}"},
                )
        elif request.form.get("library_action"):
            action = request.form.get("library_action")
            status = request.form.get("status") or "watched"
            if action == "add":
                payload, status_code = api_request(
                    "post",
                    f"/api/content/{content_id}/library",
                    json={"status": status},
                    headers={"Authorization": f"Bearer {access}"},
                )
            else:
                payload, status_code = api_request(
                    "delete",
                    f"/api/content/{content_id}/library",
                    headers={"Authorization": f"Bearer {access}"},
                )
        elif request.form.get("score"):
            score = request.form.get("score")
            payload, status = api_request(
                "post",
                f"/api/content/{content_id}/ratings",
                json={"score": score},
                headers={"Authorization": f"Bearer {access}"},
            )
        else:
            body = request.form.get("body")
            payload, status = api_request(
                "post",
                f"/api/content/{content_id}/reviews",
                json={"body": body},
                headers={"Authorization": f"Bearer {access}"},
            )

        if status in (200, 201):
            flash("İşlem başarıyla kaydedildi.", "success")
        else:
            flash(payload.get("message", "İşlem yapılamadı."), "danger")
        # reload page
        return redirect(request.path)

    payload, status = api_request("get", f"/api/content/{content_id}")
    if status == 404:
        return render_template("content_detail.html", content=None), 404
    if status != 200:
        abort(status)
    return render_template(
        "content_detail.html",
        content=payload.get("content"),
        comments=payload.get("comments", []),
    )


@app.route("/profile/<username>")
def profile(username: str):
    headers = None
    auth = session.get("auth", {})
    access = auth.get("access_token")
    if access:
        headers = {"Authorization": f"Bearer {access}"}
    payload, status = api_request("get", f"/api/profiles/{username}", headers=headers)
    if status == 404:
        return render_template("profile.html", profile=None), 404
    if status != 200:
        abort(status)

    return render_template(
        "profile.html",
        profile=payload.get("profile"),
        library_tabs=payload.get("library", {}),
        featured_lists=payload.get("featured_lists", []),
        activities=payload.get("recent_activities", []),
        is_following=payload.get("is_following", False),
    )




@app.route('/follow/<username>', methods=['POST'])
def follow(username: str):
    auth = session.get('auth', {})
    access = auth.get('access_token')
    if not access:
        flash('Giriş yapmalısınız', 'warning')
        return redirect(url_for('login'))
    payload, status = api_request('post', f'/api/users/{username}/follow', headers={'Authorization': f'Bearer {access}'})
    if status in (200,201):
        flash('Takip edildi', 'success')
    else:
        flash(payload.get('message','İşlem başarısız'), 'danger')
    return redirect(url_for('profile', username=username))


@app.route('/unfollow/<username>', methods=['POST'])
def unfollow(username: str):
    auth = session.get('auth', {})
    access = auth.get('access_token')
    if not access:
        flash('Giriş yapmalısınız', 'warning')
        return redirect(url_for('login'))
    payload, status = api_request('delete', f'/api/users/{username}/follow', headers={'Authorization': f'Bearer {access}'})
    if status == 200:
        flash('Takipten çıkıldı', 'info')
    else:
        flash(payload.get('message','İşlem başarısız'), 'danger')
    return redirect(url_for('profile', username=username))


@app.route('/activity/<int:activity_id>/like', methods=['POST'])
def activity_like(activity_id: int):
    auth = session.get('auth', {})
    access = auth.get('access_token')
    if not access:
        flash('Lütfen önce giriş yapın.', 'warning')
        return redirect(url_for('login'))

    payload, status = api_request('post', f'/api/activities/{activity_id}/like', headers={'Authorization': f'Bearer {access}'})
    if status in (200, 201):
        flash('Beğenildi', 'success')
    else:
        flash(payload.get('message', 'İşlem başarısız'), 'danger')
    # redirect back
    return redirect(request.referrer or url_for('feed'))


@app.route("/logout")
def logout():
    session.pop("auth", None)
    flash("Görüşmek üzere!", "info")
    return redirect(url_for("feed"))


init_app(app)


if __name__ == "__main__":
    app.run(debug=True)

