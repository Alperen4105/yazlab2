import os
from pathlib import Path


class BaseConfig:
    """Default configuration shared across environments."""

    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    INSTANCE_PATH = PROJECT_ROOT / "instance"
    INSTANCE_PATH.mkdir(parents=True, exist_ok=True)

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{INSTANCE_PATH / 'app.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JSON_SORT_KEYS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False

