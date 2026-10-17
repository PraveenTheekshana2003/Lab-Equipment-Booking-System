"""Pytest fixtures for Lab Equipment Booking System."""

import pytest
import os
import tempfile
from main import app as flask_app, db, User, Equipment


@pytest.fixture(scope="session")
def app():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    # Point at a fresh temp DB before any engine is created for the default path
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    flask_app.config["TESTING"] = True
    flask_app.config["SECRET_KEY"] = "test-secret-key"

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture(autouse=True)
def clean_db(app):
    """Reset tables between tests."""
    with app.app_context():
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        staff = User(username="staff", email="staff@test.com", role="staff")
        staff.set_password("staffpass")
        student = User(username="student",
                       email="student@test.com", role="student")
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
    client.post(
        "/login", data={"username": "student", "password": "studentpass"})
    return client
