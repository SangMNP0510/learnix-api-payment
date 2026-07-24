from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

credential_path = os.getenv("FIREBASE_CREDENTIALS")

if credential_path is None:
    raise RuntimeError("FIREBASE_CREDENTIALS is not configured.")

SERVICE_ACCOUNT_PATH = BASE_DIR / credential_path

if not SERVICE_ACCOUNT_PATH.exists():
    raise FileNotFoundError(
        f"Firebase credential not found: {SERVICE_ACCOUNT_PATH}"
    )

if not firebase_admin._apps:
    cred = credentials.Certificate(str(SERVICE_ACCOUNT_PATH))
    firebase_admin.initialize_app(cred)

db = firestore.client()