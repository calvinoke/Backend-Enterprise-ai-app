from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.auth.dependencies import get_auth_service
from app.auth.service import AuthService

from app.auth.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
)

from app.users.schemas import (
    UserCreate,
    UserResponse,
)


router = APIRouter(
    tags=["Authentication"],
)



@router.post(
    "/register",
    response_model=UserResponse,
)
async def register(
    data: UserCreate,
    service: AuthService = Depends(
        get_auth_service
    ),
):

    try:

        return await service.register(
            data
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )



@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    data: LoginRequest,
    service: AuthService = Depends(
        get_auth_service
    ),
):

    try:

        return await service.login(
            data.email,
            data.password,
        )


    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )



@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh_token(
    data: RefreshTokenRequest,
    service: AuthService = Depends(
        get_auth_service
    ),
):

    try:

        return await service.refresh(
            data.refresh_token
        )


    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )



@router.post(
    "/logout",
)
async def logout(
    data: RefreshTokenRequest,
    service: AuthService = Depends(
        get_auth_service
    ),
):

    try:

        return await service.logout(
            data.refresh_token
        )


    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )