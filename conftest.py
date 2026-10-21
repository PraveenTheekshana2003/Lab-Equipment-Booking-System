"""Pytest fixtures – CI-safe version."""

import os
import tempfile

import pytest

from main import Equipment, User, db

# Import ALL models so create_all() builds every table (including bookings)
from main import app as flask_app


@pytest.fixture(scope="session")
def app():
    """One temporary database for the whole test session."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    flask_app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{path}",
            "SECRET_KEY": "test-secret-key",
        }
    )

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture(autouse=True)
def clean_db(app):
    """Reset data before every test."""
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()

        staff = User(username="staff", email="staff@test.com", role="staff")
        staff.set_password("staffpass")

        student = User(username="student", email="student@test.com", role="student")
        student.set_password("studentpass")

        eq = Equipment(
            name="Test Pi",
            category="SBC",
            description="Test equipment",
            status="Available",
            image="raspberry-pi.jpg",
        )
        eq_oos = Equipment(
            name="Broken Scope",
            category="Test",
            description="Out of service item",
            status="Out of service",
        )

        db.session.add_all([staff, student, eq, eq_oos])
        db.session.commit()

    yield


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def staff_client(client):
    client.post("/login", data={"username": "staff", "password": "staffpass"})
    return client


@pytest.fixture
def student_client(client):
    client.post("/login", data={"username": "student", "password": "studentpass"})
    return client