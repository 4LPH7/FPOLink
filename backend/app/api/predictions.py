from fastapi import APIRouter

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


@router.get("/forecast")
def get_forecast():
    return {"forecast": []}
