"""FR-00 – Accounts and Login tests."""

from main import User


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data or b"Sign In" in response.data or b"login" in response.data


def test_register_page_loads(client):
    response = client.get("/register")
    assert response.status_code == 200


def test_register_user_success(client, app):
    response = client.post(
        "/register",
        data={
            "username": "newstudent",
            "email": "newstudent@test.com",
            "password": "securepass123",
            "confirm_password": "securepass123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(username="newstudent").first()
        assert user is not None
        assert user.role == "student"
        assert user.check_password("securepass123")


def test_register_duplicate_username(client):
    # First registration
    client.post(
        "/register",
        data={
            "username": "dupuser",
            "email": "dup1@test.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )
    # Duplicate username
    response = client.post(
        "/register",
        data={
            "username": "dupuser",
            "email": "dup2@test.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"already" in response.data.lower() or b"taken" in response.data.lower()


def test_login_success(client):
    # Register first
    client.post(
        "/register",
        data={
            "username": "loginstudent",
            "email": "loginstudent@test.com",
            "password": "securepass123",
            "confirm_password": "securepass123",
        },
        follow_redirects=True,
    )
    # Login
    response = client.post(
        "/login",
        data={
            "username": "loginstudent",
            "password": "securepass123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Welcome" in response.data or b"Dashboard" in response.data or b"dashboard" in response.data


def test_login_invalid_password(client):
    response = client.post(
        "/login",
        data={
            "username": "student",          # seeded user
            "password": "wrongpassword",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid" in response.data or b"invalid" in response.data or b"incorrect" in response.data.lower()


def test_logout(student_client):
    response = student_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200


def test_student_cannot_access_staff_route(student_client):
    """Students must not access staff-only pages (FR-00)."""
    response = student_client.get("/equipment/add", follow_redirects=True)
    assert response.status_code == 200
    # Should be redirected or shown access denied
    assert b"Staff" in response.data or b"staff" in response.data or b"required" in response.data.lower() or b"Dashboard" in response.data