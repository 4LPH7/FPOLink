from fastapi import APIRouter

router = APIRouter(prefix="/api/prices", tags=["prices"])

@router.get("/latest")
def get_latest_prices():
    return {"prices": {}}
