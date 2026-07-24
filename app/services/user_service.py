from datetime import datetime, timezone

from app.repositories.user_repository import (
    UserRepository,
)


class UserService:

    def __init__(self):

        self.repository = (
            UserRepository()
        )

    def is_pro(
        self,
        user_id: str,
    ) -> bool:

        subscription = (
            self.repository
            .get_subscription(
                user_id
            )
        )

        if not subscription:
            return False

        expire = subscription.get(
            "expireDate"
        )

        if not expire:
            return False

        return (
            expire >
            datetime.now(
                timezone.utc
            )
        )

    def get_subscription(
        self,
        user_id: str,
    ):

        subscription = (
            self.repository
            .get_subscription(
                user_id
            )
        )

        if not subscription:

            return {
                "isPro": False,
            }

        expire = subscription.get(
            "expireDate"
        )

        is_pro = False

        if expire:

            is_pro = (
                expire >
                datetime.now(
                    timezone.utc
                )
            )

        subscription["isPro"] = is_pro

        return subscription