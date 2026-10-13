from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.auth.dependencies import get_auth_service
from app.auth.service import AuthService

from app.auth.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
)

from app.auth.dependencies import get_current_user

from app.auth.password_reset_service import (
    PasswordResetService,
)
from app.users.models import User
from app.auth.schemas import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)

from app.users.schemas import (
    UserCreate,
    UserResponse,
)

#from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.email_verification_service import (
    EmailVerificationService,
)

from app.auth.password_service import (
    PasswordService,
)

from app.auth.schemas import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
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



# =========================================
# FORGOT PASSWORD
# =========================================

@router.post(
    "/password/forgot",
    response_model=ForgotPasswordResponse,
)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> ForgotPasswordResponse:

    service = PasswordResetService(db)

    await service.request_password_reset(
        data
    )

    # --------------------------------------
    # IMPORTANT:
    # Always return the same message.
    # This prevents account enumeration.
    # --------------------------------------

    return ForgotPasswordResponse(
        message=(
            "If an account exists for this email, "
            "a password reset link has been sent."
        )
    )


# =========================================
# RESET PASSWORD
# =========================================

@router.post(
    "/password/reset",
    response_model=ResetPasswordResponse,
)
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> ResetPasswordResponse:

    service = PasswordResetService(db)

    try:

        await service.reset_password(
            data
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return ResetPasswordResponse(
        message=(
            "Password reset successful. "
            "You can now log in with your new password."
        )
    )

# =========================================
# CHANGE PASSWORD
# =========================================

@router.post(
    "/password/change",
    response_model=ChangePasswordResponse,
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db),
) -> ChangePasswordResponse:

    service = PasswordService(db)

    try:

        await service.change_password(
            user=current_user,
            data=data,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return ChangePasswordResponse(
        message=(
            "Password changed successfully. "
            "Please log in again on your other sessions."
        )
    )


# =========================================
# VERIFY EMAIL
# =========================================

@router.post(
    "/email/verify",
    response_model=VerifyEmailResponse,
)
async def verify_email(
    data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
) -> VerifyEmailResponse:

    service = EmailVerificationService(db)

    try:

        await service.verify_email(
            data
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return VerifyEmailResponse(
        message=(
            "Email address verified successfully."
        )
    )


# =========================================
# RESEND VERIFICATION
# =========================================

@router.post(
    "/email/resend-verification",
    response_model=ResendVerificationResponse,
)
async def resend_verification(
    data: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
) -> ResendVerificationResponse:

    service = EmailVerificationService(db)

    await service.send_verification(
        str(data.email)
    )

    # --------------------------------------
    # Always return the same response.
    # --------------------------------------

    return ResendVerificationResponse(
        message=(
            "If the account exists and has not "
            "been verified, a new verification "
            "email has been sent."
        )
    )