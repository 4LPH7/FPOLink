"""API v1 router aggregator."""

from fastapi import APIRouter

from app.api.v1.crops import router as crops_router
from app.api.v1.geography import router as geography_router
from app.api.v1.markets import router as markets_router

router = APIRouter(prefix="/api/v1")
router.include_router(geography_router)
router.include_router(crops_router)
router.include_router(markets_router)
