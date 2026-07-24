from datetime import (
    datetime,
    timezone,
)

from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_current_user,
)

from app.repositories.user_repository import (
    UserRepository,
)


router = APIRouter(
    prefix="/user",
    tags=["User"],
)


@router.get(
    "/me/subscription"
)
def get_my_subscription(
    current_user: dict = Depends(
        get_current_user
    ),
):

    user_id = current_user["uid"]

    repository = UserRepository()

    subscription = (
        repository.get_subscription(
            user_id
        )
    )

    if subscription is None:

        return {
            "success": True,
            "user_id": user_id,
            "subscription": {
                "isPro": False,
                "package": None,
                "paymentId": None,
                "startDate": None,
                "expireDate": None,
            },
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

    return {
        "success": True,
        "user_id": user_id,
        "subscription": subscription,
    }