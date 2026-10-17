"""FR-00 – Accounts and Login tests (form-based routes)."""


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data or b"Sign In" in response.data


def test_register_user(client):
    response = client.post(
        "/register",
        data={
            "username": "student1",
            "email": "student1@test.com",
            "password": "securepassword123",
            "confirm_password": "securepassword123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    # After successful register we land on login (or see success message)
    assert (
        b"Registration successful" in response.data
        or b"Login" in response.data
        or b"Sign In" in response.data
    )


def test_login_user(client):
    # Register first
    client.post(
        "/register",
        data={
            "username": "student2",
            "email": "student2@test.com",
            "password": "securepassword123",
            "confirm_password": "securepassword123",
        },
        follow_redirects=True,
    )

    # Then login
    response = client.post(
        "/login",
        data={
            "username": "student2",
            "password": "securepassword123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Welcome" in response.data or b"Dashboard" in response.data


def test_login_invalid_password(client):
    client.post(
        "/register",
        data={
            "username": "student3",
            "email": "student3@test.com",
            "password": "securepassword123",
            "confirm_password": "securepassword123",
        },
        follow_redirects=True,
    )

    response = client.post(
        "/login",
        data={
            "username": "student3",
            "password": "wrongpassword",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid" in response.data or b"password" in response.data.lower()


def test_logout(student_client):
    response = student_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200