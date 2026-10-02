from datetime import UTC, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.email_verification_service import EmailVerificationService
from app.auth.models import RefreshToken
from app.auth.repository import RefreshTokenRepository
from app.auth.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.core.config import settings
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate
from app.users.enums import UserRole

# ============================================================
# AUTHENTICATION SERVICE
# ============================================================

class AuthService:
    """
    Authentication business logic.

    This service handles:

    - User registration
    - User login
    - Access token creation
    - Refresh token creation
    - Access token renewal
    - Logout
    - Email verification initiation
    """

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        db: AsyncSession,
    ):
        """
        Initialize the authentication service.

        Parameters:
            db:
                Active SQLAlchemy asynchronous database session.
        """

        self.db = db

        # User repository
        self.users = UserRepository(db)

        # Refresh token repository
        self.refresh_tokens = RefreshTokenRepository(db)

    # ========================================================
    # REGISTER
    # ========================================================

    async def register(
        self,
        data: UserCreate,
    ) -> User:
        """
        Register a new user.

        The user's password is hashed before being stored.

        A verification email is generated after the user has
        successfully been created.
        """

        # ----------------------------------------------------
        # Normalize email
        # ----------------------------------------------------

        email = (
            str(data.email)
            .strip()
            .lower()
        )

        # ----------------------------------------------------
        # Check whether email already exists
        # ----------------------------------------------------

        existing_user = await self.users.get_by_email(
            email
        )

        if existing_user:
            raise ValueError(
                "Email already registered"
            )

        # ----------------------------------------------------
        # Create user
        # ----------------------------------------------------

        user = User(
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            email=email,
            password_hash=hash_password(
                data.password
            ),
            role=UserRole.USER.value,
            is_active=True,
            is_verified=False,
        )

        # ----------------------------------------------------
        # Save user
        # ----------------------------------------------------

        user = await self.users.create(
            user
        )

        # ----------------------------------------------------
        # Send email verification
        # ----------------------------------------------------

        verification_service = EmailVerificationService(
            self.db
        )

        await verification_service.send_verification(
            user.email
        )

        # ----------------------------------------------------
        # Return created user
        # ----------------------------------------------------

        return user

    # ========================================================
    # LOGIN
    # ========================================================

    async def login(
        self,
        email: str,
        password: str,
    ) -> dict:
        """
        Authenticate a user and generate access and refresh
        tokens.
        """

        # ----------------------------------------------------
        # Normalize email
        # ----------------------------------------------------

        email = (
            email
            .strip()
            .lower()
        )

        # ----------------------------------------------------
        # Find user
        # ----------------------------------------------------

        user = await self.users.get_by_email(
            email
        )

        if not user:
            raise ValueError(
                "Invalid credentials"
            )

        # ----------------------------------------------------
        # Check account status
        # ----------------------------------------------------

        if not user.is_active:
            raise ValueError(
                "User account is inactive"
            )

        # ----------------------------------------------------
        # Verify password
        # ----------------------------------------------------

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError(
                "Invalid credentials"
            )

        # ====================================================
        # CREATE ACCESS TOKEN
        # ====================================================

        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={
                "role": user.role,
                "email": user.email,
            },
        )

        # ====================================================
        # CREATE REFRESH TOKEN
        # ====================================================

        refresh_token = create_refresh_token(
            subject=str(user.id)
        )

        # ----------------------------------------------------
        # Store hashed refresh token
        # ----------------------------------------------------

        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(
                refresh_token
            ),
            expires_at=(
                datetime.now(UTC)
                + timedelta(
                    days=settings.REFRESH_TOKEN_EXPIRE_DAYS
                )
            ),
        )

        await self.refresh_tokens.create(
            refresh_record
        )

        # ----------------------------------------------------
        # Return authentication tokens
        # ----------------------------------------------------

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    # ========================================================
    # REFRESH ACCESS TOKEN
    # ========================================================

    async def refresh(
        self,
        refresh_token: str,
    ) -> dict:
        """
        Validate an existing refresh token and generate a new
        access token.
        """

        # ----------------------------------------------------
        # Decode JWT refresh token
        # ----------------------------------------------------

        payload = decode_refresh_token(
            refresh_token
        )

        if not payload:
            raise ValueError(
                "Invalid refresh token"
            )

        # ----------------------------------------------------
        # Hash provided refresh token
        # ----------------------------------------------------

        token_hash = hash_refresh_token(
            refresh_token
        )

        # ----------------------------------------------------
        # Find token in database
        # ----------------------------------------------------

        stored_token = await self.refresh_tokens.get_by_hash(
            token_hash
        )

        if not stored_token:
            raise ValueError(
                "Refresh token not found"
            )

        # ----------------------------------------------------
        # Check whether token has been revoked
        # ----------------------------------------------------

        if stored_token.revoked:
            raise ValueError(
                "Refresh token revoked"
            )

        # ----------------------------------------------------
        # Check expiration
        # ----------------------------------------------------

        if stored_token.expires_at <= datetime.now(UTC):
            raise ValueError(
                "Refresh token expired"
            )

        # ----------------------------------------------------
        # Get associated user
        # ----------------------------------------------------

        user = stored_token.user

        if not user:
            raise ValueError(
                "User associated with refresh token not found"
            )

        # ----------------------------------------------------
        # Check account status
        # ----------------------------------------------------

        if not user.is_active:
            raise ValueError(
                "User account is inactive"
            )

        # ====================================================
        # CREATE NEW ACCESS TOKEN
        # ====================================================

        new_access_token = create_access_token(
            subject=str(user.id),
            extra_claims={
                "role": user.role,
                "email": user.email,
            },
        )

        # ----------------------------------------------------
        # Return token response
        # ----------------------------------------------------

        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    # ========================================================
    # LOGOUT
    # ========================================================

    async def logout(
        self,
        refresh_token: str,
    ) -> dict:
        """
        Revoke a refresh token so that it can no longer be used.
        """

        # ----------------------------------------------------
        # Hash the refresh token
        # ----------------------------------------------------

        token_hash = hash_refresh_token(
            refresh_token
        )

        # ----------------------------------------------------
        # Revoke token
        # ----------------------------------------------------

        await self.refresh_tokens.revoke_by_hash(
            token_hash
        )

        # ----------------------------------------------------
        # Return success response
        # ----------------------------------------------------

        return {
            "message": "Logged out successfully"
        } 