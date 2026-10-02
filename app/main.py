from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.api.v1.api import api_router


setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "application_starting",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
    )

    # Future startup tasks:
    # - Database health check
    # - Redis connection
    # - Celery initialization
    # - AI model loading

    yield

    logger.info("application_stopping")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


@app.get("/")
async def root():
    return {"message": settings.APP_NAME}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }