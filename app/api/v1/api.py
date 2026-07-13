from fastapi import APIRouter
from app.auth.router import router as auth_router
from app.users.router import router as users_router

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


