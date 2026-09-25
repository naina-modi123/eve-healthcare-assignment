from pydantic import BaseModel

from app.models.payment import PaymentStatus


class PaymentWebhook(BaseModel):
    event_id: str
    provider_payment_id: str
    status: PaymentStatus