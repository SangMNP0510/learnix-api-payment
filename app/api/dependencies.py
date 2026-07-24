from typing import Optional

from fastapi import Header, HTTPException

from app.services.firebase_auth_service import (
    FirebaseAuthService,
)


def get_current_user(
    authorization: Optional[str] = Header(
        default=None
    ),
):

    if authorization is None:

        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
        )

    if not authorization.startswith(
        "Bearer "
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header",
        )

    id_token = authorization.split(
        " ",
        1,
    )[1]

    try:

        decoded_token = (
            FirebaseAuthService.verify_token(
                id_token
            )
        )

        return decoded_token

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid Firebase ID token",
        )