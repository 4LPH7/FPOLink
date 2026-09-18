from fastapi import APIRouter

router = APIRouter(prefix="/api/farmers", tags=["farmers"])

@router.get("/")
def get_farmers():
    return {"farmers": []}
