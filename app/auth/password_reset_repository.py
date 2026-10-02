from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import (
    PasswordResetToken,
    RefreshToken,
)
from app.users.models import User


class PasswordResetRepository:
    """
    Handles password-reset token database operations.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # =========================================
    # INVALIDATE PREVIOUS TOKENS
    # =========================================

    async def invalidate_user_tokens(
        self,
        user_id: UUID,
    ) -> None:

        await self.db.execute(
            update(PasswordResetToken)
            .where(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.used.is_(False),
            )
            .values(
                used=True,
            )
        )

    # =========================================
    # CREATE RESET TOKEN
    # =========================================

    async def create(
        self,
        token: PasswordResetToken,
    ) -> PasswordResetToken:

        self.db.add(token)

        return token

    # =========================================
    # FIND VALID RESET TOKEN
    # =========================================

    async def get_valid_token(
        self,
        token_hash: str,
        current_time: datetime,
    ) -> PasswordResetToken | None:

        result = await self.db.execute(
            select(PasswordResetToken)
            .where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used.is_(False),
                PasswordResetToken.expires_at > current_time,
            )
        )

        return result.scalar_one_or_none()

    # =========================================
    # GET USER
    # =========================================

    async def get_user(
        self,
        user_id: UUID,
    ) -> User | None:

        result = await self.db.execute(
            select(User)
            .where(
                User.id == user_id
            )
        )

        return result.scalar_one_or_none()

    # =========================================
    # REVOKE REFRESH TOKENS
    # =========================================

    async def revoke_user_refresh_tokens(
        self,
        user_id: UUID,
    ) -> None:

        await self.db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked.is_(False),
            )
            .values(
                revoked=True,
            )
        )