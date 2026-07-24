from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreatePaymentRequest(BaseModel):

    package_name: str


class CreatePaymentResponse(BaseModel):

    checkout_url: str

    qr_code: str

    order_code: int

    payment_link_id: str

    amount: int

    package_name: str


class PaymentOrder(BaseModel):

    order_code: int

    user_id: str

    package_name: str

    amount: int

    status: str

    checkout_url: Optional[str] = None

    payment_link_id: Optional[str] = None

    created_at: datetime

    updated_at: datetime

    paid_at: Optional[datetime] = None