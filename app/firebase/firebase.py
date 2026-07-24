import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

SERVICE_ACCOUNT_PATH = (
    BASE_DIR
    / "credentials"
    / "firebase-service-account.json"
)

cred = credentials.Certificate(str(SERVICE_ACCOUNT_PATH))

firebase_admin.initialize_app(cred)

db = firestore.client()