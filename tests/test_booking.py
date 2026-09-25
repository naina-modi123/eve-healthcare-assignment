def get_auth_headers(client):
    client.post(
        "/auth/signup",
        json={
            "full_name": "Booking Test User",
            "email": "booking@example.com",
            "password": "Test@12345",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "booking@example.com",
            "password": "Test@12345",
        },
    )

    token = login_response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_create_booking(client):
    headers = get_auth_headers(client)

    centre_response = client.post(
        "/diagnostic-centres/",
        headers=headers,
        json={
            "name": "Test Diagnostics",
            "location": "Bhopal",
        },
    )
    assert centre_response.status_code == 201

    test_response = client.post(
        "/diagnostic-centres/tests/",
        headers=headers,
        json={
            "name": "Blood Sugar Test",
            "description": "Test for blood glucose level",
        },
    )
    assert test_response.status_code == 201

    centre_id = centre_response.json()["id"]
    test_id = test_response.json()["id"]

    centre_test_response = client.post(
        "/diagnostic-centres/centre-tests/",
        headers=headers,
        json={
            "centre_id": centre_id,
            "test_id": test_id,
            "price": 300,
        },
    )
    assert centre_test_response.status_code == 201

    booking_response = client.post(
        "/bookings/",
        headers=headers,
        json={
            "centre_id": centre_id,
            "test_id": test_id,
            "appointment_at": "2026-10-10T10:00:00+05:30",
        },
    )

    assert booking_response.status_code == 201

    booking = booking_response.json()

    assert float(booking["amount"]) == 300.0
    assert booking["status"] == "PENDING"
def test_user_cannot_cancel_another_users_booking(client):
    headers, booking_id = get_auth_headers(client), None

    centre_response = client.post(
        "/diagnostic-centres/",
        headers=headers,
        json={
            "name": "Unauthorized Test Centre",
            "location": "Bhopal",
        },
    )

    test_response = client.post(
        "/diagnostic-centres/tests/",
        headers=headers,
        json={
            "name": "Unauthorized Blood Test",
            "description": "Test for ownership validation",
        },
    )

    centre_id = centre_response.json()["id"]
    test_id = test_response.json()["id"]

    client.post(
        "/diagnostic-centres/centre-tests/",
        headers=headers,
        json={
            "centre_id": centre_id,
            "test_id": test_id,
            "price": 250,
        },
    )

    booking_response = client.post(
        "/bookings/",
        headers=headers,
        json={
            "centre_id": centre_id,
            "test_id": test_id,
            "appointment_at": "2026-10-20T10:00:00+05:30",
        },
    )

    booking_id = booking_response.json()["id"]

    client.post(
        "/auth/signup",
        json={
            "full_name": "Other User",
            "email": "other@example.com",
            "password": "Test@12345",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "other@example.com",
            "password": "Test@12345",
        },
    )

    other_headers = {
        "Authorization": f"Bearer {login_response.json()['access_token']}"
    }

    response = client.patch(
        f"/bookings/{booking_id}/cancel",
        headers=other_headers,
    )

    assert response.status_code == 404