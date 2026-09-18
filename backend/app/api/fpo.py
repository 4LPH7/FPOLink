from fastapi import APIRouter

router = APIRouter(prefix="/api/fpos", tags=["fpos"])

@router.get("/")
def get_fpos():
    return {"fpos": []}
