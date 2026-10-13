from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.database.session import get_db
from app.auth.service import AuthService
from app.users.repository import UserRepository
from app.users.models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)



async def get_auth_service(
    db: AsyncSession = Depends(get_db)
):

    return AuthService(db)



async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials"
    )


    try:

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[
                settings.ALGORITHM
            ]
        )


        user_id = payload.get("sub")


        if user_id is None:
            raise credentials_exception


    except JWTError:

        raise credentials_exception



    repository = UserRepository(db)


    user = await repository.get_by_id(
        user_id
    )


    if user is None:
        raise credentials_exception


    return user


async def require_admin(
    current_user: User = Depends(
        get_current_user
    ),
) -> User:
    """
    Require the authenticated user to have
    administrator privileges.

    This dependency is used to protect
    administrator-only API endpoints.
    """

    role = (
        current_user.role.value
        if isinstance(
            current_user.role,
            UserRole,
        )
        else str(current_user.role)
    )

    if role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Administrator privileges are required."
            ),
        )

    return current_user