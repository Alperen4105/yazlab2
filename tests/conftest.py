import os
import sys

# Ensure repository root is on sys.path so tests can import app and backend modules
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest


@pytest.fixture(autouse=True)
def reset_db():
    """Reset the database before each test to a consistent seeded state.

    This ensures tests are isolated and do not depend on side-effects
    from previous tests which persist in the development SQLite file.
    """
    from app import app
    from backend.extensions import db

    with app.app_context():
        # drop & recreate all tables and seed with development fixtures
        db.drop_all()
        db.create_all()
        try:
            from backend.fixtures import seed_from_sample_data

            seed_from_sample_data()
        except Exception:
            # don't fail tests if seeding breaks - tests may adjust
            pass
        yield
