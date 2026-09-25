def setup_booking(client):
    client.post(
        "/auth/signup",
        json={
            "full_name": "Payment Test User",
            "email": "payment@example.com",
            "password": "Test@12345",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "payment@example.com",
            "password": "Test@12345",
        },
    )

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    centre_response = client.post(
        "/diagnostic-centres/",
        headers=headers,
        json={
            "name": "Payment Diagnostics",
            "location": "Bhopal",
        },
    )

    test_response = client.post(
        "/diagnostic-centres/tests/",
        headers=headers,
        json={
            "name": "Payment Blood Test",
            "description": "Test for payment flow",
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
            "price": 500,
        },
    )

    booking_response = client.post(
        "/bookings/",
        headers=headers,
        json={
            "centre_id": centre_id,
            "test_id": test_id,
            "appointment_at": "2026-10-15T10:00:00+05:30",
        },
    )

    return headers, booking_response.json()["id"]


def test_successful_payment_confirms_booking(client):
    headers, booking_id = setup_booking(client)

    payment_response = client.post(
        "/payments/",
        headers=headers,
        json={
            "booking_id": booking_id,
            "status": "SUCCESS",
        },
    )

    assert payment_response.status_code == 201
    assert payment_response.json()["status"] == "SUCCESS"

    bookings_response = client.get(
        "/bookings/",
        headers=headers,
    )

    assert bookings_response.status_code == 200

    booking = bookings_response.json()[0]

    assert booking["id"] == booking_id
    assert booking["status"] == "CONFIRMED"
def test_failed_payment_marks_booking_failed(client):
    headers, booking_id = setup_booking(client)

    payment_response = client.post(
        "/payments/",
        headers=headers,
        json={
            "booking_id": booking_id,
            "status": "FAILED",
        },
    )

    assert payment_response.status_code == 201
    assert payment_response.json()["status"] == "FAILED"

    bookings_response = client.get(
        "/bookings/",
        headers=headers,
    )

    assert bookings_response.status_code == 200

    booking = bookings_response.json()[0]

    assert booking["id"] == booking_id
    assert booking["status"] == "FAILED"

def test_webhook_is_idempotent(client):
    headers, booking_id = setup_booking(client)

    payment_response = client.post(
        "/payments/",
        headers=headers,
        json={
            "booking_id": booking_id,
            "status": "SUCCESS",
        },
    )

    assert payment_response.status_code == 201

    payment = payment_response.json()
    provider_payment_id = payment["provider_payment_id"]

    webhook_payload = {
        "event_id": "evt_test_idempotent_001",
        "provider_payment_id": provider_payment_id,
        "status": "SUCCESS",
    }

    first_webhook = client.post(
        "/payments/webhook/",
        json=webhook_payload,
    )

    assert first_webhook.status_code == 200
    assert first_webhook.json()["message"] == "Webhook processed successfully"

    second_webhook = client.post(
        "/payments/webhook/",
        json=webhook_payload,
    )

    assert second_webhook.status_code == 200
    assert second_webhook.json()["message"] == "Webhook event already processed"
def test_duplicate_payment_is_rejected(client):
    headers, booking_id = setup_booking(client)

    first_payment = client.post(
        "/payments/",
        headers=headers,
        json={
            "booking_id": booking_id,
            "status": "SUCCESS",
        },
    )

    assert first_payment.status_code == 201

    second_payment = client.post(
        "/payments/",
        headers=headers,
        json={
            "booking_id": booking_id,
            "status": "SUCCESS",
        },
    )

    assert second_payment.status_code == 400
    assert second_payment.json()["detail"] == (
        "Payment can only be made for a pending booking"
    )