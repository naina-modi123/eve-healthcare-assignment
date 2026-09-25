# EVE Healthcare Diagnostic Booking API

Backend service for diagnostic test bookings and simulated payments.

## Overview

This project provides REST APIs for:

- User signup and JWT-based authentication
- Diagnostic centre management
- Diagnostic test management
- Centre-test availability and pricing
- Diagnostic test bookings
- Simulated successful and failed payments
- Payment webhooks with idempotent event handling
- Booking cancellation
- Automated API tests

## Tech Stack

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT
- Pytest
- Swagger / OpenAPI

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/signup` | Register a new user |
| POST | `/auth/login` | Login and receive JWT |
| GET | `/auth/me` | Get current authenticated user |

### Diagnostic Centres & Tests

| Method | Endpoint | Description |
|---|---|---|
| POST | `/diagnostic-centres/` | Create a diagnostic centre |
| GET | `/diagnostic-centres/` | List active diagnostic centres |
| POST | `/diagnostic-centres/tests/` | Create a diagnostic test |
| GET | `/diagnostic-centres/tests/` | List diagnostic tests |
| POST | `/diagnostic-centres/centre-tests/` | Add a test to a centre with price |

### Bookings

| Method | Endpoint | Description |
|---|---|---|
| POST | `/bookings/` | Create a diagnostic booking |
| GET | `/bookings/` | Get current user's bookings |
| PATCH | `/bookings/{booking_id}/cancel` | Cancel a booking |

### Payments

| Method | Endpoint | Description |
|---|---|---|
| POST | `/payments/` | Simulate a payment |
| POST | `/payments/webhook/` | Process payment webhook |

## API Examples

### 1. Signup

```http
POST /auth/signup
Content-Type: application/json
```

```json
{
  "full_name": "Test Patient",
  "email": "test@example.com",
  "password": "Test@12345"
}
```

Example response:

```json
{
  "id": 1,
  "full_name": "Test Patient",
  "email": "test@example.com",
  "is_active": true
}
```

---

### 2. Login

```http
POST /auth/login
Content-Type: application/json
```

```json
{
  "email": "test@example.com",
  "password": "Test@12345"
}
```

Example response:

```json
{
  "access_token": "<jwt_access_token>",
  "token_type": "bearer"
}
```

Use the token for protected endpoints:

```http
Authorization: Bearer <access_token>
```

---

### 3. Get Current User

```http
GET /auth/me
Authorization: Bearer <access_token>
```

Example response:

```json
{
  "id": 1,
  "full_name": "Test Patient",
  "email": "test@example.com",
  "is_active": true
}
```

---

### 4. Create a Diagnostic Centre

```http
POST /diagnostic-centres/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "name": "Apollo Diagnostics",
  "location": "Bhopal, Madhya Pradesh"
}
```

Example response:

```json
{
  "id": 1,
  "name": "Apollo Diagnostics",
  "location": "Bhopal, Madhya Pradesh",
  "is_active": true
}
```

---

### 5. Get Diagnostic Centres

```http
GET /diagnostic-centres/
```

Example response:

```json
[
  {
    "id": 1,
    "name": "Apollo Diagnostics",
    "location": "Bhopal, Madhya Pradesh",
    "is_active": true
  }
]
```

---

### 6. Create a Diagnostic Test

```http
POST /diagnostic-centres/tests/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "name": "Complete Blood Count",
  "description": "A blood test used to evaluate overall health."
}
```

Example response:

```json
{
  "id": 1,
  "name": "Complete Blood Count",
  "description": "A blood test used to evaluate overall health."
}
```

---

### 7. Get Diagnostic Tests

```http
GET /diagnostic-centres/tests/
```

Example response:

```json
[
  {
    "id": 1,
    "name": "Complete Blood Count",
    "description": "A blood test used to evaluate overall health."
  }
]
```

---

### 8. Add a Test to a Diagnostic Centre

```http
POST /diagnostic-centres/centre-tests/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "centre_id": 1,
  "test_id": 1,
  "price": 500
}
```

Example response:

```json
{
  "id": 1,
  "centre_id": 1,
  "test_id": 1,
  "price": 500.0,
  "is_available": true
}
```

The same diagnostic test cannot be added more than once to the same centre.

---

### 9. Create a Booking

```http
POST /bookings/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "centre_id": 1,
  "test_id": 1,
  "appointment_at": "2026-10-01T10:00:00+05:30"
}
```

Example response:

```json
{
  "id": 1,
  "user_id": 1,
  "centre_id": 1,
  "test_id": 1,
  "appointment_at": "2026-10-01T10:00:00+05:30",
  "amount": "500.00",
  "status": "PENDING"
}
```

The booking amount is determined by the centre-test price stored in the database rather than being supplied by the client.

---

### 10. Get My Bookings

```http
GET /bookings/
Authorization: Bearer <access_token>
```

Example response:

```json
[
  {
    "id": 1,
    "user_id": 1,
    "centre_id": 1,
    "test_id": 1,
    "appointment_at": "2026-10-01T10:00:00+05:30",
    "amount": "500.00",
    "status": "PENDING"
  }
]
```

---

### 11. Simulate a Successful Payment

```http
POST /payments/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "booking_id": 1,
  "status": "SUCCESS"
}
```

Example response:

```json
{
  "id": 1,
  "booking_id": 1,
  "amount": 500.0,
  "status": "SUCCESS",
  "provider_payment_id": "mock_<generated_id>"
}
```

A successful payment changes the booking status:

```text
PENDING -> CONFIRMED
```

---

### 12. Simulate a Failed Payment

```http
POST /payments/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "booking_id": 2,
  "status": "FAILED"
}
```

A failed payment changes the booking status:

```text
PENDING -> FAILED
```

---

### 13. Payment Webhook

```http
POST /payments/webhook/
Content-Type: application/json
```

```json
{
  "event_id": "evt_test_001",
  "provider_payment_id": "mock_payment_id",
  "status": "SUCCESS"
}
```

The webhook updates the payment and corresponding booking status.

Webhook events are idempotent. Repeating the same `event_id` does not create another payment or process the event again.

---

### 14. Cancel a Booking

```http
PATCH /bookings/1/cancel
Authorization: Bearer <access_token>
```

Example response:

```json
{
  "id": 1,
  "user_id": 1,
  "centre_id": 1,
  "test_id": 1,
  "appointment_at": "2026-10-01T10:00:00+05:30",
  "amount": "500.00",
  "status": "CANCELLED"
}
```

A user can only cancel their own booking.

## Project Structure

```text
eve-healthcare-assignment/
│
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── booking.py
│   │   ├── diagnostic.py
│   │   └── payment.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   └── dependencies.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── diagnostic_centre.py
│   │   ├── diagnostic_test.py
│   │   ├── centre_test.py
│   │   ├── booking.py
│   │   └── payment.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── diagnostic.py
│   │   ├── booking.py
│   │   ├── payment.py
│   │   └── webhook.py
│   │
│   └── main.py
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_booking.py
│   └── test_payment.py
│
├── alembic/
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── README.md
```

## Database Design

The application uses PostgreSQL with SQLAlchemy ORM and Alembic migrations.

### Main Tables

- `users` — stores registered users and password hashes
- `diagnostic_centres` — stores diagnostic centre information
- `diagnostic_tests` — stores available diagnostic tests
- `centre_tests` — maps tests to centres and stores test prices
- `bookings` — stores user bookings, appointment time, amount, and status
- `payments` — stores payment information and webhook identifiers

### Booking Statuses

```text
PENDING
CONFIRMED
FAILED
CANCELLED
```

### Payment Statuses

```text
SUCCESS
FAILED
```

## Authentication

The API uses JWT-based authentication.

Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

Passwords are stored as bcrypt hashes and are never returned in API responses.

## Webhook Idempotency

Payment webhook events contain a unique `event_id`.

If the same webhook event is received again, the API detects the previously processed event and returns the existing payment information instead of processing it again.

This prevents duplicate payment processing and inconsistent booking states.

## Validation and Edge Cases

The API handles:

- Invalid authentication credentials
- Duplicate user registration
- Invalid booking IDs
- Future appointment validation
- Tests unavailable at a selected centre
- Duplicate centre-test combinations
- Payment attempts for non-pending bookings
- Failed payments
- Repeated webhook events
- Unauthorized booking modifications
- Booking cancellation rules

## Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd eve-healthcare-assignment
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/eve_healthcare
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
```

Do not commit `.env` to GitHub.

Use `.env.example` as the configuration template.

### 5. Create the database

Create a PostgreSQL database named:

```text
eve_healthcare
```

Make sure PostgreSQL is running before starting the application.

### 6. Run database migrations

```powershell
alembic upgrade head
```

### 7. Start the API

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## Swagger / OpenAPI Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

## Running Tests

Run the complete test suite with:

```powershell
pytest
```

Current test coverage includes:

- User signup
- User login
- Duplicate signup prevention
- Booking creation
- Successful payment
- Failed payment
- Webhook idempotency
- Duplicate payment prevention
- Unauthorized booking modification

Expected result:

```text
9 passed
```

## Docker

Docker support files are included:

- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

Docker Compose can be used to run the API with PostgreSQL.

```bash
docker compose up --build
```

Then run migrations inside the API container:

```bash
docker compose exec api alembic upgrade head
```

If Docker is not installed locally, the application can still be run directly using Python, FastAPI, and PostgreSQL as described in the Setup section.

## Assumptions

- Diagnostic centre/test management endpoints require authentication for modifications.
- Diagnostic centre and test retrieval endpoints are publicly accessible.
- A booking can only be created when the selected test is available at the selected centre.
- Booking amount is taken from the configured centre-test price.
- Appointment time must be in the future.
- A booking can have only one payment.
- A payment can be processed only while the booking is `PENDING`.
- Payment processing is simulated rather than connected to a real payment provider.
- Webhook `event_id` is used for idempotent event handling.
- Users can only view and modify their own bookings.

## Future Improvements

Possible future improvements include:

- Redis-based caching
- Celery background jobs
- Rate limiting
- Structured logging
- Pagination for list endpoints
- Webhook retry handling
- Real payment gateway integration
- Role-based access control for diagnostic centre administration
- Appointment slot availability management
- Docker-based production deployment
- CI/CD pipeline

## License

This project was developed as part of the EVE Healthcare SDE Intern Hiring Assignment.
```

**One important thing:** I deliberately used placeholders such as `<your-github-repository-url>`, `<jwt_access_token>`, and `your_password`. **Do not put your actual password, JWT secret, or access token anywhere in the README.**