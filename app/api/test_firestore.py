from fastapi import APIRouter

from app.firebase.firebase import db

router = APIRouter(
    prefix="/test",
    tags=["Test"],
)


@router.get("/firestore")
def test_firestore():

    db.collection("test").document("hello").set(
        {
            "message": "Firebase Connected"
        }
    )

    return {
        "success": True
    }