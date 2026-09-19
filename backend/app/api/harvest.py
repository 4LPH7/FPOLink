from fastapi import APIRouter

router = APIRouter(prefix="/api/harvest", tags=["harvest"])


@router.get("/")
def get_harvests():
    return {"harvests": []}
