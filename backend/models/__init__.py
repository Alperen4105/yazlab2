"""SQLAlchemy models reflecting the documented schema."""

from backend.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100))
    avatar_url = db.Column(db.Text)
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    followers = db.relationship(
        "Follow",
        foreign_keys="Follow.followed_id",
        backref="followed",
        lazy="dynamic",
    )
    following = db.relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        backref="follower",
        lazy="dynamic",
    )

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Follow(db.Model):
    __tablename__ = "follows"

    follower_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    followed_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())


class Content(db.Model):
    __tablename__ = "contents"

    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(120), index=True)
    content_type = db.Column(db.Enum("movie", "book", name="content_type"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    synopsis = db.Column(db.Text)
    release_year = db.Column(db.SmallInteger)
    runtime_minutes = db.Column(db.SmallInteger)
    page_count = db.Column(db.SmallInteger)
    cover_url = db.Column(db.Text)
    extra_metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())


class LibraryItem(db.Model):
    __tablename__ = "library_items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content_id = db.Column(
        db.Integer, db.ForeignKey("contents.id", ondelete="CASCADE"), nullable=False
    )
    status = db.Column(
        db.Enum(
            "watched",
            "watchlist",
            "read",
            "reading_list",
            name="library_status",
        ),
        nullable=False,
    )
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    user = db.relationship("User", backref=db.backref("library_items", lazy="dynamic"))
    content = db.relationship("Content", backref="library_entries")


class CustomList(db.Model):
    __tablename__ = "custom_lists"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    visibility = db.Column(
        db.Enum("public", "private", "followers", name="list_visibility"),
        nullable=False,
        server_default="public",
    )
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    owner = db.relationship("User", backref=db.backref("custom_lists", lazy="dynamic"))


class CustomListItem(db.Model):
    __tablename__ = "custom_list_items"

    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(
        db.Integer, db.ForeignKey("custom_lists.id", ondelete="CASCADE"), nullable=False
    )
    content_id = db.Column(
        db.Integer, db.ForeignKey("contents.id", ondelete="CASCADE"), nullable=False
    )
    order_index = db.Column(db.Integer, default=0)

    list = db.relationship(
        "CustomList",
        backref=db.backref("items", lazy="dynamic", order_by=order_index, cascade="all, delete-orphan"),
    )
    content = db.relationship("Content")


class Rating(db.Model):
    __tablename__ = "ratings"
    __table_args__ = (
        db.UniqueConstraint("user_id", "content_id", name="uq_rating_user_content"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content_id = db.Column(
        db.Integer, db.ForeignKey("contents.id", ondelete="CASCADE"), nullable=False
    )
    score = db.Column(db.SmallInteger, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    user = db.relationship("User", backref=db.backref("ratings", lazy="dynamic"))
    content = db.relationship("Content", backref=db.backref("ratings", lazy="dynamic"))


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content_id = db.Column(
        db.Integer, db.ForeignKey("contents.id", ondelete="CASCADE"), nullable=False
    )
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

    user = db.relationship("User", backref=db.backref("reviews", lazy="dynamic"))
    content = db.relationship("Content", backref=db.backref("reviews", lazy="dynamic"))


class ReviewReaction(db.Model):
    __tablename__ = "review_reactions"
    __table_args__ = (
        db.UniqueConstraint("review_id", "user_id", name="uq_review_reaction"),
    )

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(
        db.Integer, db.ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    reaction_type = db.Column(
        db.Enum("like", "dislike", name="reaction_type"), nullable=False
    )
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    review = db.relationship("Review", backref=db.backref("reactions", lazy="dynamic"))
    user = db.relationship("User")


class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    activity_type = db.Column(
        db.Enum(
            "rating",
            "review",
            "list_add",
            "library_status",
            name="activity_type",
        ),
        nullable=False,
    )
    related_id = db.Column(db.Integer)
    extra_metadata = db.Column(db.JSON)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    user = db.relationship("User", backref=db.backref("activities", lazy="dynamic"))


class PasswordReset(db.Model):
    __tablename__ = "password_resets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    used = db.Column(db.Boolean, default=False, nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    user = db.relationship("User", backref=db.backref("password_resets", lazy="dynamic"))

