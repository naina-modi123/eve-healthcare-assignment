from pydantic import BaseModel, ConfigDict, Field

from app.models.payment import PaymentStatus


class PaymentCreate(BaseModel):
    booking_id: int
    status: PaymentStatus


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    amount: float
    status: PaymentStatus
    provider_payment_id: str

    model_config = ConfigDict(from_attributes=True)