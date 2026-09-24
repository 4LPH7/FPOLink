"""API v1 router aggregator."""

from fastapi import APIRouter

from app.api.v1.geography import router as geography_router

router = APIRouter(prefix="/api/v1")
router.include_router(geography_router)
