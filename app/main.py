from fastapi import FastAPI

from app.api.payment import router as payment_router
from app.api.test_firestore import router as test_router
from app.api.webhook import router as webhook_router
from app.api.user import router as user_router
from fastapi.middleware.cors import (
    CORSMiddleware
)


app = FastAPI(
    title="Learnix Payment API"
)


app.include_router(
    payment_router
)

app.include_router(
    test_router
)

app.include_router(
    webhook_router
)

app.include_router(
    user_router
)

app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "*"
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)


@app.get("/")
def root():

    return {
        "message":
            "Learnix Payment API"
    }