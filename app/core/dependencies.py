from typing import Callable

from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.users.models import User


def require_role(required_role: str) -> Callable:
    """
    Create a dependency that requires the authenticated user
    to have a specific role.
    """

    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )

        return current_user

    return role_checker


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Require the authenticated user to have the admin role.
    """

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required.",
        )

    return current_user