from fastapi import APIRouter

router = APIRouter(prefix="/api/buyers", tags=["buyers"])

@router.get("/")
def get_buyers():
    return {"buyers": []}
