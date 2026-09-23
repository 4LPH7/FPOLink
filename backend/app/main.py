import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "fpolink-api", "version": "0.1.0"}
