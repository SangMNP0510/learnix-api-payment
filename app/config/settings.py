from dotenv import load_dotenv
import os

load_dotenv()

PAYOS_CLIENT_ID = os.getenv("PAYOS_CLIENT_ID")
PAYOS_API_KEY = os.getenv("PAYOS_API_KEY")
PAYOS_CHECKSUM_KEY = os.getenv("PAYOS_CHECKSUM_KEY")

RETURN_URL = "http://localhost:3000/payment-success"

CANCEL_URL = "http://localhost:3000/payment-cancel"