from dotenv import load_dotenv
import os

load_dotenv()

PAYOS_CLIENT_ID = os.getenv("PAYOS_CLIENT_ID")
PAYOS_API_KEY = os.getenv("PAYOS_API_KEY")
PAYOS_CHECKSUM_KEY = os.getenv("PAYOS_CHECKSUM_KEY")

RETURN_URL = os.getenv(
    "RETURN_URL"
)

CANCEL_URL = os.getenv(
    "CANCEL_URL"
)