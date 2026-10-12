import pytest
from main import app, db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


def test_index_page(client):
    """Test that the index/login page loads successfully."""
    response = client.get("/")
    assert response.status_code == 200


def test_user_login_flow(client):
    """Test login functionality for students and staff."""
    response = client.get("/login")
    assert response.status_code in [200, 302]


def test_register_user(client):
    response = client.post(
        "/api/register",
        json={
            "username": "student1",
            "email": "student1@test.com",
            "password": "securepassword123",
            "role": "student",
        },
    )
    assert response.status_code == 201
    assert response.get_json()["message"] == "User registered successfully"


def test_login_user(client):
    client.post(
        "/api/register",
        json={
            "username": "student1",
            "email": "student1@test.com",
            "password": "securepassword123",
            "role": "student",
        },
    )

    response = client.post(
        "/api/login",
        json={"username": "student1", "password": "securepassword123"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Login successful"
    assert data["username"] == "student1"
    assert data["role"] == "student"


def test_login_invalid_password(client):
    client.post(
        "/api/register",
        json={
            "username": "student1",
            "email": "student1@test.com",
            "password": "securepassword123",
            "role": "student",
        },
    )

    response = client.post(
        "/api/login",
        json={"username": "student1", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "error" in response.get_json()