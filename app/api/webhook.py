from fastapi import APIRouter, Request, HTTPException

from app.services.payos_service import PayOSService
from app.services.webhook_service import WebhookService
from app.utils.logger import (
    logger,
)
from app.repositories.payment_repository import PaymentRepository
from app.models.payment_status import PaymentStatus
from datetime import datetime, timezone


router = APIRouter(
    prefix="/webhook",
    tags=["Webhook"],
)


@router.post("/payos")
async def payos_webhook(
    request: Request,
):
    """
    PayOS Webhook Endpoint

    Flow:

    PayOS
        ↓
    POST /webhook/payos
        ↓
    Đọc raw body
        ↓
    Parse JSON
        ↓
    Verify signature
        ↓
    Kiểm tra payment code
        ↓
    Tìm payment trong Firestore
        ↓
    Update payment SUCCESS
        ↓
    Mở Pro subscription
        ↓
    Trả HTTP 200
    """

    # =====================================================
    # 1. Đọc raw request body
    # =====================================================

    raw_body = await request.body()

    if not raw_body:

        raise HTTPException(
            status_code=400,
            detail="Webhook body is empty",
        )


    logger.info("=" * 60)
    logger.info("PAYOS WEBHOOK RECEIVED")
    logger.info("=" * 60)


    logger.info("Raw body:")

    logger.info(
        raw_body.decode(
            "utf-8",
            errors="replace",
        )
    )


    # =====================================================
    # 2. Parse JSON
    # =====================================================

    try:

        payload = await request.json()
        logger.info(f"PayOS webhook payload: {payload}")

    except Exception as e:

        logger.info(
            "========== WEBHOOK JSON PARSE ERROR =========="
        )

        logger.info(
            str(e)
        )

        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload",
        )


    logger.info(
        "Parsed payload:"
    )

    logger.info(
        payload
    )


    # =====================================================
    # 3. Verify PayOS signature
    # =====================================================

    try:

        payos_service = PayOSService()

        webhook_data = (
            payos_service.verify_webhook(
                payload
            )
        )


    except Exception as e:

        logger.info("=" * 60)
        logger.info("PAYOS WEBHOOK VERIFY FAILED")
        logger.info("=" * 60)

        logger.info(
            f"Error: {str(e)}"
        )

        return {
            "success": True,
            "message": "Webhook received",
        }


    logger.info("=" * 60)
    logger.info("PAYOS WEBHOOK VERIFIED")
    logger.info("=" * 60)


    logger.info(
    f"Order Code: {webhook_data.order_code}"
    )

    logger.info(
        f"Amount: {webhook_data.amount}"
    )

    logger.info(
        f"Code: {webhook_data.code}"
    )

    logger.info(
        f"Description: {webhook_data.desc}"
    )


    # =====================================================
    # 4. Kiểm tra giao dịch thành công
    # =====================================================

    if webhook_data.code != "00":

        logger.info(
            "========== PAYMENT NOT SUCCESS =========="
        )
        
        PaymentRepository().update(
            webhook_data.order_code,
            {
                "status": PaymentStatus.FAILED.value,
                "updated_at": datetime.now(timezone.utc),
            },
        )


        # Webhook đã được nhận và verify thành công.
        #
        # Tuy nhiên giao dịch không thành công.
        #
        # Trả 200 để PayOS biết backend
        # đã nhận và xử lý webhook.

        return {

            "success":
                True,

            "message":
                "Payment is not successful",

            "order_code":
                webhook_data.order_code,
        }


    # =====================================================
    # 5. Xử lý thanh toán thành công
    # =====================================================

    try:

        service = WebhookService()


        result = (
            service.process_success_payment(

                order_code=(
                    webhook_data.order_code
                ),

                paid_amount=(
                    webhook_data.amount
                ),
            )
        )


        logger.info(
            "========== PAYMENT BUSINESS RESULT =========="
        )


        logger.info(
            result
        )


        # =================================================
        # 6. Payment không tồn tại
        #
        # Có thể là webhook test của PayOS
        # =================================================

        if result.get(
            "ignored"
        ) is True:

            logger.info(
                "========== WEBHOOK IGNORED =========="
            )


            return {

                "success":
                    True,

                "message":
                    "Webhook received but payment was not found",

                "order_code":
                    webhook_data.order_code,
            }


        # =================================================
        # 7. Payment đã xử lý hoặc xử lý thành công
        # =================================================

        logger.info("=" * 60)
        logger.info("PAYMENT PROCESSED SUCCESSFULLY")
        logger.info("=" * 60)


        return {

            "success":
                True,

            "message":
                result.get(
                    "message",
                    "Webhook processed successfully",
                ),

            "order_code":
                webhook_data.order_code,
        }


    # =====================================================
    # 8. Business Error
    # =====================================================

    except ValueError as e:

        logger.info(
            "========== PAYMENT BUSINESS ERROR =========="
        )


        logger.info(
            str(e)
        )


        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


    # =====================================================
    # 9. System Error
    # =====================================================

    except Exception as e:

        logger.exception(
            "PAYMENT PROCESSING FAILED"
        )

        return {
            "success": True,
            "message": "Webhook received",
        }