import json
import os

import firebase_admin

from firebase_admin import (
    credentials,
    firestore,
)

cred = credentials.Certificate(
    json.loads(
        os.environ[
            "FIREBASE_CREDENTIALS"
        ]
    )
)

firebase_admin.initialize_app(
    cred
)

db = firestore.client()