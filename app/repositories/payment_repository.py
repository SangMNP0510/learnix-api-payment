from app.firebase.firebase import db

from app.models.payment import PaymentOrder


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