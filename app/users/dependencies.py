from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.users.enums import UserRole
from app.users.models import User


# ============================================================
# REQUIRE ADMIN
# ============================================================

async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allow access only to administrators.
    """

    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )

    return current_user


# ============================================================
# REQUIRE SELF OR ADMIN
# ============================================================

async def require_self_or_admin(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Allow the request when:

    1. The authenticated user is accessing their own user ID.
    2. The authenticated user is an administrator.
    """

    is_admin = (
        current_user.role == UserRole.ADMIN.value
    )

    is_owner = (
        current_user.id == user_id
    )

    if not is_admin and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own user record.",
        )

    return current_user