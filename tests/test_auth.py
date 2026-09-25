def test_signup(client):
    response = client.post(
        "/auth/signup",
        json={
            "full_name": "Test Patient",
            "email": "pytest@example.com",
            "password": "Test@12345",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["full_name"] == "Test Patient"
    assert data["email"] == "pytest@example.com"
    assert "password_hash" not in data
def test_login(client):
    client.post(
        "/auth/signup",
        json={
            "full_name": "Login Test User",
            "email": "login@example.com",
            "password": "Test@12345",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "Test@12345",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
def test_duplicate_signup(client):
    payload = {
        "full_name": "Duplicate User",
        "email": "duplicate@example.com",
        "password": "Test@12345",
    }

    first_response = client.post("/auth/signup", json=payload)
    assert first_response.status_code == 201

    second_response = client.post("/auth/signup", json=payload)
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Email is already registered"