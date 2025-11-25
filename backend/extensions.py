from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def init_extensions(app):
    """Attach shared extensions to the Flask app instance."""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

