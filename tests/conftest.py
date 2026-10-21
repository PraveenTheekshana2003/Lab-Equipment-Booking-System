"""
Pytest fixtures – force-login via session so tests never depend on the login form.
Uses a temporary file DB so every request sees the same data.
"""

import os
import tempfile

import pytest

from main import User, db, seed_data
from main import app as flask_app


@pytest.fixture
def app():
    """Fresh temporary SQLite database for each test."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    flask_app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "WTF_CSRF_ENABLED": False,
            "SECRET_KEY": "test-secret-key",
            "SERVER_NAME": "localhost",
        }
    )

    with flask_app.app_context():
        db.session.remove()
        db.engine.dispose()
        db.create_all()
        seed_data()
        yield flask_app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()

    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture
def client(app):
    """Anonymous test client."""
    return app.test_client()


def _force_login(client, app, username: str):
    """Log in by writing Flask-Login session keys (most reliable in tests)."""
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        assert user is not None, f"Seeded user '{username}' not found"
        user_id = user.id

    with client.session_transaction() as sess:
        # Flask-Login keys
        sess["_user_id"] = str(user_id)
        sess["_fresh"] = True

    return client


@pytest.fixture
def student_client(app, client):
    """Client logged in as seeded student."""
    return _force_login(client, app, "student")


@pytest.fixture
def staff_client(app, client):
    """Client logged in as seeded staff."""
    return _force_login(client, app, "staff")