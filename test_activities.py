"""Test activity creation"""
from app import app
from backend.models import Activity, Content, User
from backend.extensions import db

with app.app_context():
    # Check recent activities
    recent = Activity.query.order_by(Activity.created_at.desc()).limit(5).all()
    print(f"Total activities in DB: {Activity.query.count()}")
    print(f"\nRecent 5 activities:")
    for act in recent:
        user = User.query.get(act.user_id)
        content = Content.query.get(act.related_id) if act.related_id else None
        print(f"  - {user.username} did {act.activity_type} on {content.title if content else 'N/A'} at {act.created_at}")
        print(f"    Extra: {act.extra_metadata}")
    
    # Check if we have users
    print(f"\nTotal users: {User.query.count()}")
    users = User.query.limit(3).all()
    for u in users:
        print(f"  - {u.username} (id: {u.id})")
    
    # Check contents
    print(f"\nTotal content: {Content.query.count()}")
    contents = Content.query.limit(5).all()
    for c in contents:
        print(f"  - {c.title} ({c.external_id or f'content-{c.id}'})")
