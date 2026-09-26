from fastapi import APIRouter

from app.api.v1.audit import router as audit_router
from app.api.v1.buyers import router as buyers_router
from app.api.v1.commodities import router as commodities_router
from app.api.v1.crops import router as crops_router
from app.api.v1.farmers import router as farmers_router
from app.api.v1.farms import router as farms_router
from app.api.v1.fpos import router as fpos_router
from app.api.v1.geography import router as geography_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.intelligence import router as intelligence_router
from app.api.v1.markets import router as markets_router
from app.api.v1.matching import router as matching_router
from app.api.v1.prices import router as prices_router

router = APIRouter(prefix="/api/v1")
router.include_router(geography_router)
router.include_router(crops_router)
router.include_router(commodities_router)
router.include_router(markets_router)
router.include_router(prices_router)
router.include_router(ingestion_router)
router.include_router(intelligence_router)
router.include_router(farmers_router)
router.include_router(farms_router)
router.include_router(buyers_router)
router.include_router(matching_router)
router.include_router(fpos_router)
router.include_router(audit_router)
