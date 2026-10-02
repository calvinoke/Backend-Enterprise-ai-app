from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from uuid import UUID

from app.auth.models import PasswordResetToken
from app.auth.password_reset_repository import (
    PasswordResetRepository,
)
from app.auth.security import (
    generate_password_reset_token,
    hash_password,
    hash_password_reset_token,
)
from app.auth.schemas import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.notifications.email_service import (
    send_password_reset_email,
)
from app.users.repository import UserRepository


PASSWORD_RESET_EXPIRY_MINUTES = 15


class PasswordResetService:
    """
    Handles forgot-password and password-reset operations.
    """

    def __init__(
        self,
        db,
    ):
        self.password_reset_repository = (
            PasswordResetRepository(db)
        )

        self.user_repository = (
            UserRepository(db)
        )

        self.db = db

    # =========================================
    # FORGOT PASSWORD
    # =========================================

    async def request_password_reset(
        self,
        data: ForgotPasswordRequest,
    ) -> None:

        email = str(
            data.email
        ).strip().lower()

        user = (
            await self.user_repository.get_by_email(
                email
            )
        )

        # --------------------------------------
        # ALWAYS RETURN GENERIC RESULT
        # --------------------------------------
        #
        # Do not expose whether the email exists.
        # --------------------------------------

        if not user:
            return

        # --------------------------------------
        # INVALIDATE OLD TOKENS
        # --------------------------------------

        await (
            self.password_reset_repository
            .invalidate_user_tokens(
                user.id
            )
        )

        # --------------------------------------
        # GENERATE RAW TOKEN
        # --------------------------------------

        raw_token = (
            generate_password_reset_token()
        )

        # --------------------------------------
        # HASH TOKEN
        # --------------------------------------

        token_hash = (
            hash_password_reset_token(
                raw_token
            )
        )

        # --------------------------------------
        # EXPIRATION
        # --------------------------------------

        now = datetime.now(
            timezone.utc
        )

        expires_at = (
            now
            + timedelta(
                minutes=PASSWORD_RESET_EXPIRY_MINUTES
            )
        )

        # --------------------------------------
        # STORE TOKEN HASH
        # --------------------------------------

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False,
        )

        await (
            self.password_reset_repository
            .create(reset_token)
        )

        await self.db.commit()

        # --------------------------------------
        # BUILD FRONTEND RESET URL
        # --------------------------------------

        import os

        frontend_url = os.getenv(
            "FRONTEND_URL",
            "http://localhost:5173",
        ).rstrip("/")

        reset_link = (
            f"{frontend_url}/reset-password"
            f"?token={quote(raw_token)}"
        )

        # --------------------------------------
        # SEND RESET EMAIL
        # --------------------------------------

        try:

            await send_password_reset_email(
                to_email=user.email,
                reset_link=reset_link,
                expires_minutes=(
                    PASSWORD_RESET_EXPIRY_MINUTES
                ),
            )

        except Exception as exc:

            print(
                "Password reset email failed:",
                exc,
            )

            # Do not reveal account existence
            # to the API caller.
            #
            # In production, this should also
            # be monitored/alerted.

    # =========================================
    # RESET PASSWORD
    # =========================================

    async def reset_password(
        self,
        data: ResetPasswordRequest,
    ) -> None:

        token_hash = (
            hash_password_reset_token(
                data.token
            )
        )

        now = datetime.now(
            timezone.utc
        )

        reset_token = (
            await self.password_reset_repository
            .get_valid_token(
                token_hash=token_hash,
                current_time=now,
            )
        )

        if not reset_token:
            raise ValueError(
                "Invalid or expired password reset token."
            )

        # --------------------------------------
        # FIND USER
        # --------------------------------------

        user = (
            await self.password_reset_repository
            .get_user(
                reset_token.user_id
            )
        )

        if not user:
            raise ValueError(
                "Invalid or expired password reset token."
            )

        # --------------------------------------
        # UPDATE PASSWORD
        # --------------------------------------

        user.password_hash = (
            hash_password(
                data.new_password
            )
        )

        # --------------------------------------
        # CONSUME TOKEN
        # --------------------------------------

        reset_token.used = True

        # --------------------------------------
        # REVOKE EXISTING SESSIONS
        # --------------------------------------

        await (
            self.password_reset_repository
            .revoke_user_refresh_tokens(
                user.id
            )
        )

        # --------------------------------------
        # COMMIT TRANSACTION
        # --------------------------------------

        await self.db.commit()