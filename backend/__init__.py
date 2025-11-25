from flask import Flask

from backend.api import api_bp
from backend.config import DevelopmentConfig
from backend.extensions import init_extensions


def init_app(app: Flask, config_object=DevelopmentConfig) -> None:
    """Configure Flask app with extensions and blueprints."""
    app.config.from_object(config_object)
    init_extensions(app)
    app.register_blueprint(api_bp)

