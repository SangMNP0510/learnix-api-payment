from app.firebase.firebase import db


class UserRepository:

    COLLECTION = "users"

    def update_subscription(
        self,
        user_id: str,
        subscription: dict,
    ):

        (
            db.collection(
                self.COLLECTION
            )
            .document(
                user_id
            )
            .set(
                {
                    "subscription": subscription
                },
                merge=True,
            )
        )


    def get_subscription(
        self,
        user_id: str,
    ):

        doc = (
            db.collection(
                self.COLLECTION
            )
            .document(
                user_id
            )
            .get()
        )

        if not doc.exists:
            return None

        data = doc.to_dict()

        return data.get(
            "subscription"
        )