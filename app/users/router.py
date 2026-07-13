from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
from app.users.models import User


router = APIRouter()


@router.get("/me")
async def profile(
    user: User = Depends(
        get_current_user
    )
):

    return {
        "id": str(user.id),
        "email": user.email,
        "role": user.role,
        "message": "Authenticated user"
    }