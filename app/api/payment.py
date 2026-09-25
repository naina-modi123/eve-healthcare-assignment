from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.dependencies import get_db
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = (
        db.query(Booking)
        .filter(
            Booking.id == payment_data.booking_id,
            Booking.user_id == current_user.id,
        )
        .first()
    )

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment can only be made for a pending booking",
        )

    existing_payment = (
        db.query(Payment)
        .filter(Payment.booking_id == booking.id)
        .first()
    )

    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment already exists for this booking",
        )

    payment = Payment(
        booking_id=booking.id,
        amount=booking.amount,
        status=payment_data.status,
        provider_payment_id=f"mock_{uuid4().hex}",
    )

    if payment_data.status.value == "SUCCESS":
        booking.status = BookingStatus.CONFIRMED
    else:
        booking.status = BookingStatus.FAILED

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment
from app.schemas.webhook import PaymentWebhook


@router.post("/webhook/")
def payment_webhook(
    webhook_data: PaymentWebhook,
    db: Session = Depends(get_db),
):
    existing_event = (
        db.query(Payment)
        .filter(Payment.webhook_event_id == webhook_data.event_id)
        .first()
    )

    if existing_event:
        return {
            "message": "Webhook event already processed",
            "payment_id": existing_event.id,
            "status": existing_event.status,
        }

    payment = (
        db.query(Payment)
        .filter(
            Payment.provider_payment_id
            == webhook_data.provider_payment_id
        )
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    payment.webhook_event_id = webhook_data.event_id
    payment.status = webhook_data.status

    if webhook_data.status.value == "SUCCESS":
        payment.booking.status = BookingStatus.CONFIRMED
    else:
        payment.booking.status = BookingStatus.FAILED

    db.commit()

    return {
        "message": "Webhook processed successfully",
        "payment_id": payment.id,
        "status": payment.status,
    }