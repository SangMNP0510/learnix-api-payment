from payos import PayOS
from payos.types import CreatePaymentLinkRequest

from app.config.settings import (
    PAYOS_CLIENT_ID,
    PAYOS_API_KEY,
    PAYOS_CHECKSUM_KEY,
)


class PayOSService:

    def __init__(self):

        self.payos = PayOS(
            client_id=PAYOS_CLIENT_ID,
            api_key=PAYOS_API_KEY,
            checksum_key=PAYOS_CHECKSUM_KEY,
        )

    def create_payment_link(
        self,
        payment_data: CreatePaymentLinkRequest,
    ):

        response = self.payos.payment_requests.create(
            payment_data
        )

        return {
            "checkout_url": response.checkout_url,
            "qr_code": response.qr_code,
            "order_code": response.order_code,
            "payment_link_id": response.payment_link_id,
        }
        
    def verify_webhook(
        self,
        payload: dict,
    ):
        return self.payos.webhooks.verify(payload)