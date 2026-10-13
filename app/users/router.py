from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.users.dependencies import (
    require_admin,
    require_self_or_admin,
)
from app.users.models import User
from app.users.schemas import (
    AdminUserCreate,
    UserResponse,
    UserRoleUpdate,
    UserUpdate,
)
from app.users.service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ============================================================
# GET CURRENT USER
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Return the currently authenticated user's profile.
    """

    return UserResponse.model_validate(
        current_user
    )


# ============================================================
# UPDATE CURRENT USER
# ============================================================

@router.patch(
    "/me",
    response_model=UserResponse,
)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Allow an authenticated user to update their own profile.
    """

    service = UserService(db)

    try:
        user = await service.update_user(
            user=current_user,
            data=data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return UserResponse.model_validate(
        user
    )


# ============================================================
# GET ALL USERS - ADMIN ONLY
# ============================================================

@router.get(
    "",
    response_model=list[UserResponse],
)
async def get_users(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=100,
    ),
    _current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[UserResponse]:
    """
    Return a paginated list of users.

    Administrator access only.
    """

    service = UserService(db)

    users = await service.get_users(
        skip=skip,
        limit=limit,
    )

    return [
        UserResponse.model_validate(user)
        for user in users
    ]


# ============================================================
# CREATE USER - ADMIN ONLY
# ============================================================

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    data: AdminUserCreate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Allow an administrator to create a new user.

    The administrator can choose the initial role.
    """

    service = UserService(db)

    try:
        user = await service.create_user(
            current_admin=current_admin,
            data=data,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return UserResponse.model_validate(
        user
    )


# ============================================================
# GET USER BY ID
# ============================================================

@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(
    user_id: UUID,
    _current_user: User = Depends(require_self_or_admin),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Return a specific user.

    A normal user can retrieve only their own record.
    Administrators can retrieve any user.
    """

    service = UserService(db)

    try:
        user = await service.get_user_by_id(
            user_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return UserResponse.model_validate(
        user
    )


# ============================================================
# UPDATE USER BY ID
# ============================================================

@router.patch(
    "/{user_id}",
    response_model=UserResponse,
)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    _current_user: User = Depends(require_self_or_admin),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Update a user.

    A normal user can update only their own record.
    Administrators can update any user.

    Role is deliberately not included in UserUpdate.
    """

    service = UserService(db)

    try:
        user = await service.get_user_by_id(
            user_id
        )

        user = await service.update_user(
            user=user,
            data=data,
        )

    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if str(exc) == "User not found."
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc

    return UserResponse.model_validate(
        user
    )


# ============================================================
# UPDATE USER ROLE - ADMIN ONLY
# ============================================================

@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
)
async def update_user_role(
    user_id: UUID,
    data: UserRoleUpdate,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Change the role of a user.

    Administrator access only.

    An administrator can promote a user to admin
    or demote an admin to user, subject to the
    business rules enforced by UserService.
    """

    service = UserService(db)

    try:
        user = await service.update_user_role(
            current_admin=current_admin,
            target_user_id=user_id,
            role=data.role,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if str(exc) == "User not found."
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc

    return UserResponse.model_validate(
        user
    )


# ============================================================
# ACTIVATE USER - ADMIN ONLY
# ============================================================

@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
)
async def activate_user(
    user_id: UUID,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Activate a user account.

    Administrator access only.
    """

    service = UserService(db)

    try:
        user = await service.activate_user(
            current_admin=current_admin,
            target_user_id=user_id,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return UserResponse.model_validate(
        user
    )


# ============================================================
# DEACTIVATE USER - ADMIN ONLY
# ============================================================

@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
)
async def deactivate_user(
    user_id: UUID,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Deactivate a user account.

    Administrator access only.

    Business rules such as protecting the last
    active administrator are enforced by UserService.
    """

    service = UserService(db)

    try:
        user = await service.deactivate_user(
            current_admin=current_admin,
            target_user_id=user_id,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if str(exc) == "User not found."
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc

    return UserResponse.model_validate(
        user
    )


# ============================================================
# DELETE USER - ADMIN ONLY
# ============================================================

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: UUID,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Permanently delete a user.

    Administrator access only.

    Business rules such as preventing deletion of
    the last active administrator are enforced by
    UserService.
    """

    service = UserService(db)

    try:
        await service.delete_user(
            current_admin=current_admin,
            target_user_id=user_id,
        )

    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if str(exc) == "User not found."
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(exc),
        ) from exc

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
