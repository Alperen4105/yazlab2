from flask import Flask

from backend.api import api_bp
from backend.config import DevelopmentConfig
from backend.extensions import init_extensions, db
from sqlalchemy import inspect


def init_app(app: Flask, config_object=DevelopmentConfig) -> None:
    """Configure Flask app with extensions and blueprints."""
    app.config.from_object(config_object)
    init_extensions(app)
    app.register_blueprint(api_bp)
    # If running in development and the database is empty, create tables so
    # the local development experience works without running migrations.
    # This is intentionally conservative: it only creates tables when there
    # are no tables yet and we're in development mode.
    if app.config.get("DEBUG"):
        with app.app_context():
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            if not existing_tables:
                app.logger.info("No database tables found, creating all tables for development.")
                db.create_all()
                # after creating tables, populate a small dataset for local testing
                try:
                    from backend.fixtures import seed_from_sample_data

                    # only seed if there are no users
                    from backend.models import User

                    if User.query.count() == 0:
                        app.logger.info("Seeding database with sample data for development.")
                        seed_from_sample_data()
                except Exception:
                    # don't break startup if seeding fails; it's a developer convenience
                    app.logger.exception("DB seeding failed (development only)")

