from datetime import datetime, timezone, timedelta

from app.models.payment_status import PaymentStatus

from app.repositories.payment_repository import (
    PaymentRepository,
)

from app.repositories.user_repository import (
    UserRepository,
)

from app.utils.logger import (
    logger,
)


class WebhookService:

    def __init__(self):

        self.payment_repository = PaymentRepository()

        self.user_repository = UserRepository()


    def process_success_payment(
        self,
        order_code: int,
        paid_amount: int,
    ):

        # =====================================
        # 1. Lấy payment từ Firestore
        # =====================================

        payment = self.payment_repository.get(
            order_code
        )


        # =====================================
        # 2. Không tìm thấy payment
        # =====================================

        if payment is None:

            logger.info(
                f"[WEBHOOK] Payment not found: {order_code}"
            )

            return {
                "success": False,
                "message": "Payment not found",
                "order_code": order_code,
                "ignored": True,
            }


        # =====================================
        # 3. Kiểm tra số tiền
        # =====================================

        if payment["amount"] != paid_amount:

            raise ValueError(
                "Payment amount does not match"
            )


        # =====================================
        # 4. Idempotency
        # =====================================

        if (
            payment["status"]
            == PaymentStatus.SUCCESS.value
        ):

            logger.info(
                f"[WEBHOOK] Payment already processed: {order_code}"
            )

            return {
                "success": True,
                "message": "Payment already processed",
                "order_code": order_code,
            }


        # =====================================
        # 5. Chỉ xử lý PENDING
        # =====================================

        if (
            payment["status"]
            != PaymentStatus.PENDING.value
        ):

            raise ValueError(
                "Payment is not in PENDING status"
            )


        # =====================================
        # 6. Thời gian hiện tại
        # =====================================

        now = datetime.now(
            timezone.utc
        )


        # =====================================
        # 7. Xác định package
        # =====================================

        package_name = payment[
            "package_name"
        ]


        # =====================================
        # 8. Lấy subscription hiện tại
        # =====================================

        current_subscription = (
            self.user_repository
            .get_subscription(
                payment["user_id"]
            )
        )


        # =====================================
        # 9. Lấy expireDate cũ
        # =====================================

        old_expire_date = None

        if current_subscription:

            old_expire_date = (
                current_subscription.get(
                    "expireDate"
                )
            )


        # =====================================
        # 10. Xác định ngày bắt đầu tính
        #
        # Nếu user vẫn còn Pro:
        #     base_date = expireDate cũ
        #
        # Nếu user chưa có Pro
        # hoặc Pro đã hết hạn:
        #     base_date = now
        # =====================================

        if (
            old_expire_date
            and old_expire_date > now
        ):

            base_date = old_expire_date

        else:

            base_date = now


        # =====================================
        # 11. Tính expireDate mới
        # =====================================

        if package_name == "pro_month":

            expire_date = (
                base_date
                + timedelta(days=30)
            )


        elif package_name == "pro_year":

            expire_date = (
                base_date
                + timedelta(days=365)
            )


        else:

            raise ValueError(
                f"Unknown package: {package_name}"
            )


        # =====================================
        # 12. Cập nhật Payment -> SUCCESS
        # =====================================

        self.payment_repository.update(

            order_code,

            {
                "status":
                    PaymentStatus.SUCCESS.value,

                "paid_at":
                    now,

                "updated_at":
                    now,
            },
        )


        # =====================================
        # 13. Mở / Gia hạn Pro cho User
        # =====================================

        self.user_repository.update_subscription(

            payment["user_id"],

            {
                "isPro": True,

                "package":
                    package_name,

                "paymentId":
                    order_code,

                "startDate":
                    now,

                "expireDate":
                    expire_date,
            },
        )


        # =====================================
        # 14. Kết quả
        # =====================================

        return {

            "success": True,

            "message":
                "Payment processed successfully",

            "order_code":
                order_code,

            "user_id":
                payment["user_id"],

            "package":
                package_name,

            "expire_date":
                expire_date.isoformat(),
        }