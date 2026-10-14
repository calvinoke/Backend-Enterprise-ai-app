
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import get_logger, setup_logging


# --------------------------------------------------
# 1. Initialize application logging
# --------------------------------------------------

setup_logging()
logger = get_logger(__name__)

logger.info("startup_diagnostic_before_api_router_import")


# --------------------------------------------------
# 2. Import API routes and diagnose import problems
# --------------------------------------------------

try:
    from app.api.v1.api import api_router

    logger.info("startup_diagnostic_after_api_router_import")

except Exception:
    logger.exception("startup_diagnostic_api_router_import_failed")
    raise


# --------------------------------------------------
# 3. Application lifespan
# --------------------------------------------------

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


# --------------------------------------------------
# 4. Create FastAPI application
# --------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


# --------------------------------------------------
# 5. Configure CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://enterprise-ai-frontend-nine.vercel.app"
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# 6. Register API routes
# --------------------------------------------------

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


# --------------------------------------------------
# 7. Root endpoint
# --------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": settings.APP_NAME,
    }


# --------------------------------------------------
# 8. Health check endpoint
# --------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }
