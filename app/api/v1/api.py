from fastapi import APIRouter
from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.aiii.router import router as ai_router

api_router = APIRouter()


api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    ai_router,
    prefix="/ai",
    tags=["AI"],
)

