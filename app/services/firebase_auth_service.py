from fastapi import HTTPException
from firebase_admin import auth


class FirebaseAuthService:

    @staticmethod
    def verify_token(
        authorization: str,
    ):

        if not authorization:

            raise HTTPException(
                status_code=401,
                detail="Authorization header is required",
            )


        if not authorization.startswith(
            "Bearer "
        ):

            raise HTTPException(
                status_code=401,
                detail="Invalid authorization format",
            )


        token = authorization.split(
            "Bearer ",
            1,
        )[1].strip()


        if not token:

            raise HTTPException(
                status_code=401,
                detail="Firebase token is empty",
            )


        try:

            decoded_token = (
                auth.verify_id_token(
                    token
                )
            )

            return decoded_token

        except Exception:

            raise HTTPException(
                status_code=401,
                detail="Invalid Firebase token",
            )