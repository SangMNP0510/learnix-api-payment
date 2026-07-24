from fastapi import HTTPException
from firebase_admin import auth


class FirebaseAuthService:

    @staticmethod
    def verify_token(
        id_token: str,
    ):

        if not id_token:

            raise HTTPException(
                status_code=401,
                detail="Firebase token is empty",
            )

        try:

            decoded_token = auth.verify_id_token(
                id_token
            )

            return decoded_token

        except Exception as e:

            print(e)

            raise HTTPException(
                status_code=401,
                detail="Invalid Firebase token",
            )