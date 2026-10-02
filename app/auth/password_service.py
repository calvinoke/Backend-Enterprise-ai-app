from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken
from app.auth.schemas import ChangePasswordRequest
from app.auth.security import (
    hash_password,
    verify_password,
    validate_password_strength,
)
from app.users.models import User


class PasswordService:
    """
    Handles authenticated password changes.
    """

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # =========================================
    # CHANGE PASSWORD
    # =========================================

    async def change_password(
        self,
        user: User,
        data: ChangePasswordRequest,
    ) -> None:

        # --------------------------------------
        # Verify current password
        # --------------------------------------

        if not verify_password(
            data.current_password,
            user.password_hash,
        ):
            raise ValueError(
                "Current password is incorrect."
            )

        # --------------------------------------
        # Prevent same password
        # --------------------------------------

        if verify_password(
            data.new_password,
            user.password_hash,
        ):
            raise ValueError(
                "New password must be different from the current password."
            )

        # --------------------------------------
        # Validate password strength
        # --------------------------------------

        validate_password_strength(
            data.new_password
        )

        # --------------------------------------
        # Hash new password
        # --------------------------------------

        user.password_hash = (
            hash_password(
                data.new_password
            )
        )

        # --------------------------------------
        # Revoke existing refresh sessions
        # --------------------------------------

        await self.db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user.id,
                RefreshToken.revoked.is_(False),
            )
            .values(
                revoked=True,
            )
        )

        # --------------------------------------
        # Commit
        # --------------------------------------

        await self.db.commit()

