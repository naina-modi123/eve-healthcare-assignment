from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.diagnostic import router as diagnostic_router
from app.api.booking import router as booking_router
from app.api.payment import router as payment_router


app = FastAPI(
    title="EVE Healthcare Diagnostic Booking API",
    description="Backend service for diagnostic test bookings and simulated payments.",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(diagnostic_router)
app.include_router(booking_router)
app.include_router(payment_router)


@app.get("/")
def root():
    return {"message": "EVE Healthcare API is running"}