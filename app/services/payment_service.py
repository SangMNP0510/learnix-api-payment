from datetime import datetime, timezone
import random
import time

from payos.types import (
    CreatePaymentLinkRequest,
    ItemData,
)

from app.config.packages import PACKAGES
from app.config.settings import (
    RETURN_URL,
    CANCEL_URL,
)

from app.models.payment import PaymentOrder
from app.models.payment_status import PaymentStatus

from app.repositories.payment_repository import PaymentRepository
from app.services.payos_service import PayOSService


class PaymentService:

    def __init__(self):

        self.repository = PaymentRepository()

        self.payos = PayOSService()


    def generate_order_code(self) -> int:

        timestamp = int(time.time())

        random_number = random.randint(
            1000,
            9999,
        )

        return int(
            f"{timestamp}{random_number}"
        )


    def get_package(
        self,
        package_name: str,
    ):

        if package_name not in PACKAGES:

            raise ValueError(
                "Package not found"
            )

        return PACKAGES[
            package_name
        ]


    def create_payment(
        self,
        user_id: str,
        package_name: str,
    ):

        # ==============================
        # 1. Lấy package
        # ==============================
        
        print("package_name =", repr(package_name))
        print("PACKAGES =", PACKAGES)

        package = self.get_package(
            package_name
        )


        # ==============================
        # 2. Generate order code
        # ==============================

        order_code = (
            self.generate_order_code()
        )


        now = datetime.now(
            timezone.utc
        )


        # ==============================
        # 3. Tạo payment PENDING
        # ==============================

        payment = PaymentOrder(

            order_code=order_code,

            user_id=user_id,

            package_name=package_name,

            amount=package["price"],

            status=PaymentStatus.PENDING.value,

            checkout_url=None,

            payment_link_id=None,

            created_at=now,

            updated_at=now,
        )


        # ==============================
        # 4. Lưu Firestore trước
        # ==============================

        self.repository.create(
            payment
        )


        # ==============================
        # 5. Tạo PayOS payment request
        # ==============================

        payment_request = (
            CreatePaymentLinkRequest(

                orderCode=order_code,

                amount=package["price"],

                description=package[
                    "description"
                ],

                returnUrl=RETURN_URL,

                cancelUrl=CANCEL_URL,

                items=[
                    ItemData(

                        name=package[
                            "description"
                        ],

                        quantity=1,

                        price=package[
                            "price"
                        ],
                    )
                ],
            )
        )


        # ==============================
        # 6. Gọi PayOS
        # ==============================

        try:

            result = (
                self.payos.create_payment_link(
                    payment_request
                )
            )

        except Exception as e:

            self.repository.update(

                order_code,

                {
                    "status":
                        PaymentStatus.FAILED.value,

                    "updated_at":
                        datetime.now(
                            timezone.utc
                        ),

                    "error_message":
                        str(e),
                },
            )

            raise


        # ==============================
        # 7. Update PayOS information
        # ==============================

        self.repository.update(

            order_code,

            {
                "checkout_url":
                    result[
                        "checkout_url"
                    ],

                "payment_link_id":
                    result[
                        "payment_link_id"
                    ],

                "updated_at":
                    datetime.now(
                        timezone.utc
                    ),
            },
        )


        # ==============================
        # 8. Return response
        # ==============================

        return {

            "checkout_url":
                result[
                    "checkout_url"
                ],

            "qr_code":
                result[
                    "qr_code"
                ],

            "order_code":
                order_code,

            "payment_link_id":
                result[
                    "payment_link_id"
                ],

            "amount":
                package[
                    "price"
                ],

            "package_name":
                package_name,
        }