from fastapi import FastAPI
from app.core.logging import setup_logging, get_logger
from app.core.config import settings


setup_logging()

logger = get_logger(__name__)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)


@app.on_event("startup")
async def startup_event():

    logger.info(
        "application_started",
        app=settings.APP_NAME,
        version=settings.APP_VERSION
    )


@app.get("/")
async def root():

    logger.info(
        "root_endpoint_called"
    )

    return {
        "message": settings.APP_NAME
    }


@app.get("/health")
async def health():

    logger.info(
        "health_check"
    )

    return {
        "status": "healthy"
    }