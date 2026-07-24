from fastapi import APIRouter, HTTPException

from app.repositories.payment_repository import (
    PaymentRepository,
)

from app.models.payment import (
    CreatePaymentRequest,
)

from app.services.payment_service import (
    PaymentService,
)

from fastapi import (
    APIRouter,
    HTTPException,
    Header,
)

from app.services.firebase_auth_service import (
    FirebaseAuthService,
)
from fastapi import APIRouter, HTTPException
from fastapi import Depends
from app.api.dependencies import get_current_user


router = APIRouter(
    prefix="/payment",
    tags=["Payment"],
)


@router.get("/ping")
def ping():

    return {
        "message": "Payment router works",
    }


@router.post("/create")
def create_payment(
    request: CreatePaymentRequest,
    current_user: dict = Depends(
        get_current_user
    ),
):
    user_id = current_user["uid"]

    service = PaymentService()

    result = service.create_payment(

        user_id=user_id,

        package_name=
            request.package_name,

    )


    return result


@router.get("/order/{order_code}")
def get_order(order_code: int):

    repository = PaymentRepository()

    payment = repository.get(order_code)

    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    return {
        "success": True,
        "data": payment,
    }