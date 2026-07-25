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
from datetime import timedelta


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
        
        pending = self.repository.get_pending_payment(user_id)

        if pending is not None:

            return {

                "checkout_url": pending["checkout_url"],

                "qr_code": None,

                "order_code": pending["order_code"],

                "payment_link_id": pending["payment_link_id"],

                "amount": pending["amount"],

                "package_name": pending["package_name"],

                "expired_at": pending["expired_at"],
            }


        # ==============================
        # 2. Generate order code
        # ==============================

        order_code = (
            self.generate_order_code()
        )


        now = datetime.now(
            timezone.utc
        )
        
        expired_at = now + timedelta(minutes=15)


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
            expired_at=expired_at,
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
                
            "expired_at": expired_at,
        }
        
    def get_order(
        self,
        order_code: int,
    ):

        payment = self.repository.get(order_code)

        if payment is None:
            return None

        now = datetime.now(timezone.utc)

        if (
            payment["status"] == PaymentStatus.PENDING.value
            and now > payment["expired_at"]
        ):

            self.repository.update(

                order_code,

                {

                    "status":
                        PaymentStatus.EXPIRED.value,

                    "updated_at":
                        now,

                },
            )

            payment["status"] = PaymentStatus.EXPIRED.value

        return payment