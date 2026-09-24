import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api import (
    admin,
    admin_whatsapp,
    auth,
    buyers,
    crops,
    farmers,
    fpo,
    harvest,
    predictions,
    prices,
    whatsapp,
)
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.SENTRY_DSN:
        try:
            import sentry_sdk

            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                environment=settings.ENVIRONMENT,
                traces_sample_rate=0.1,
            )
            logger.info("Sentry initialized (env=%s)", settings.ENVIRONMENT)
        except ImportError:
            logger.warning("sentry-sdk not installed; skipping Sentry initialization")
    logger.info("FPOLink TN API starting...")
    yield


app = FastAPI(
    title="FPOLink TN API",
    description="FPO Digital Operating System for Tamil Nadu",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1 import router as v1_router

app.include_router(auth.router)
app.include_router(fpo.router)
app.include_router(farmers.router)
app.include_router(prices.router)
app.include_router(crops.router)
app.include_router(harvest.router)
app.include_router(buyers.router)
app.include_router(predictions.router)
app.include_router(admin.router)
app.include_router(admin_whatsapp.router)
app.include_router(whatsapp.router)
app.include_router(v1_router)


@app.get("/health")
@app.get("/api/health")
def health_check():
    try:
        from app.database import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "service": "fpolink-api", "version": "0.1.0", "db": "ok"}
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "service": "fpolink-api",
                "version": "0.1.0",
                "db": "error",
                "detail": str(exc),
            },
        )
