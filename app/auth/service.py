from datetime import datetime, UTC, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    decode_refresh_token,
)

from app.auth.models import RefreshToken
from app.auth.repository import RefreshTokenRepository

from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate

from app.core.config import settings


class AuthService:
    """
    Authentication business logic.
    """


    def __init__(
        self,
        db: AsyncSession,
    ):

        self.users = UserRepository(db)

        self.refresh_tokens = RefreshTokenRepository(db)

        self.db = db



    async def register(
        self,
        data: UserCreate,
    ) -> User:


        existing = await self.users.get_by_email(
            data.email
        )


        if existing:
            raise ValueError(
                "Email already registered"
            )


        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            password_hash=hash_password(
                data.password
            ),
            role="user",
        )


        return await self.users.create(user)



    async def login(
        self,
        email: str,
        password: str,
    ):


        user = await self.users.get_by_email(
            email
        )


        if not user:
            raise ValueError(
                "Invalid credentials"
            )


        if not verify_password(
            password,
            user.password_hash,
        ):

            raise ValueError(
                "Invalid credentials"
            )


        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={
                "role": user.role,
                "email": user.email,
            },
        )


        refresh_token = create_refresh_token(
            subject=str(user.id)
        )


        refresh_record = RefreshToken(

            user_id=user.id,

            token_hash=hash_refresh_token(
                refresh_token
            ),

            expires_at=(
                datetime.now(UTC)
                +
                timedelta(
                    days=settings.REFRESH_TOKEN_EXPIRE_DAYS
                )
            ),
        )


        await self.refresh_tokens.create(
            refresh_record
        )


        return {

            "access_token": access_token,

            "refresh_token": refresh_token,

            "token_type": "bearer",
        }



    async def refresh(
        self,
        refresh_token: str,
    ):


        payload = decode_refresh_token(
            refresh_token
        )


        if not payload:

            raise ValueError(
                "Invalid refresh token"
            )


        token_hash = hash_refresh_token(
            refresh_token
        )


        stored_token = await self.refresh_tokens.get_by_hash(
            token_hash
        )


        if not stored_token:

            raise ValueError(
                "Refresh token not found"
            )


        if stored_token.revoked:

            raise ValueError(
                "Refresh token revoked"
            )


        if stored_token.expires_at < datetime.now(UTC):

            raise ValueError(
                "Refresh token expired"
            )


        user = stored_token.user


        new_access_token = create_access_token(

            subject=str(user.id),

            extra_claims={

                "role": user.role,

                "email": user.email,
            },
        )


        return {

            "access_token": new_access_token,

            "refresh_token": refresh_token,

            "token_type": "bearer",
        }



    async def logout(
        self,
        refresh_token: str,
    ):


        token_hash = hash_refresh_token(
            refresh_token
        )


        await self.refresh_tokens.revoke_by_hash(
            token_hash
        )


        return {
            "message": "Logged out successfully"
        }