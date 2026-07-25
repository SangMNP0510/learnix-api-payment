from app.firebase.firebase import db

from app.models.payment import PaymentOrder

from datetime import datetime, timezone
from app.models.payment_status import PaymentStatus


class PaymentRepository:

    COLLECTION = "payments"


    def create(
        self,
        payment: PaymentOrder,
    ):

        doc = (
            db.collection(
                self.COLLECTION
            )
            .document(
                str(
                    payment.order_code
                )
            )
        )


        doc.set(
            payment.model_dump()
        )


    def get(
        self,
        order_code: int,
    ):

        doc = (
            db.collection(
                self.COLLECTION
            )
            .document(
                str(order_code)
            )
            .get()
        )


        if not doc.exists:

            return None


        return doc.to_dict()


    def update(
        self,
        order_code: int,
        data: dict,
    ):

        doc = (
            db.collection(
                self.COLLECTION
            )
            .document(
                str(order_code)
            )
        )


        doc.update(
            data
        )
        
    def get_pending_payment(
        self,
        user_id: str,
    ):

        query = (
            db.collection(self.COLLECTION)
            .where("user_id", "==", user_id)
            .where("status", "==", PaymentStatus.PENDING.value)
            .limit(1)
            .stream()
        )

        for doc in query:

            payment = doc.to_dict()

            if payment["expired_at"] <= datetime.now(timezone.utc):

                self.update(

                    payment["order_code"],

                    {
                        "status": PaymentStatus.EXPIRED.value,
                        "updated_at": datetime.now(timezone.utc),
                    },
                )

                return None

            return payment

        return None