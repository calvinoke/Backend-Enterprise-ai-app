from datetime import datetime, timedelta, timezone
import os
from urllib.parse import quote

from app.auth.email_verification_repository import (
    EmailVerificationRepository,
)

from app.auth.models import (
    EmailVerificationToken,
)

from app.auth.schemas import (
    ResendVerificationRequest,
    VerifyEmailRequest,
)

from app.auth.security import (
    generate_email_verification_token,
    hash_email_verification_token,
)

from app.notifications.email_service import (
    send_email_verification_email,
)

from app.users.repository import UserRepository


EMAIL_VERIFICATION_EXPIRY_HOURS = 24


class EmailVerificationService:
    """
    Handles email verification and
    verification email resend operations.
    """

    def __init__(
        self,
        db,
    ):
        self.db = db

        self.repository = (
            EmailVerificationRepository(db)
        )

        self.user_repository = (
            UserRepository(db)
        )

    # =========================================
    # SEND VERIFICATION
    # =========================================

    async def send_verification(
        self,
        email: str,
    ) -> None:

        email = (
            email
            .strip()
            .lower()
        )

        user = (
            await self.user_repository.get_by_email(
                email
            )
        )

        # --------------------------------------
        # Generic behavior
        # --------------------------------------

        if not user:
            return

        if user.is_verified:
            return

        # --------------------------------------
        # Invalidate previous tokens
        # --------------------------------------

        await (
            self.repository
            .invalidate_user_tokens(
                user.id
            )
        )

        # --------------------------------------
        # Generate token
        # --------------------------------------

        raw_token = (
            generate_email_verification_token()
        )

        token_hash = (
            hash_email_verification_token(
                raw_token
            )
        )

        # --------------------------------------
        # Expiration
        # --------------------------------------

        now = datetime.now(
            timezone.utc
        )

        expires_at = (
            now
            + timedelta(
                hours=EMAIL_VERIFICATION_EXPIRY_HOURS
            )
        )

        # --------------------------------------
        # Store hashed token
        # --------------------------------------

        verification_token = (
            EmailVerificationToken(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=expires_at,
                used=False,
            )
        )

        await (
            self.repository
            .create(
                verification_token
            )
        )

        await self.db.commit()

        # --------------------------------------
        # Build frontend URL
        # --------------------------------------

        frontend_url = os.getenv(
            "FRONTEND_URL",
            "http://localhost:5173",
        ).rstrip("/")

        verification_link = (
            f"{frontend_url}"
            f"/verify-email"
            f"?token={quote(raw_token)}"
        )

        # --------------------------------------
        # Send email
        # --------------------------------------

        try:

            await send_email_verification_email(
                to_email=user.email,
                verification_link=(
                    verification_link
                ),
                expires_hours=(
                    EMAIL_VERIFICATION_EXPIRY_HOURS
                ),
            )

        except Exception as exc:

            print(
                "Verification email failed:",
                exc,
            )

    # =========================================
    # VERIFY EMAIL
    # =========================================

    async def verify_email(
        self,
        data: VerifyEmailRequest,
    ) -> None:

        token_hash = (
            hash_email_verification_token(
                data.token
            )
        )

        now = datetime.now(
            timezone.utc
        )

        verification_token = (
            await self.repository
            .get_valid_token(
                token_hash=token_hash,
                current_time=now,
            )
        )

        if not verification_token:
            raise ValueError(
                "Invalid or expired verification token."
            )

        user = (
            await self.repository
            .get_user(
                verification_token.user_id
            )
        )

        if not user:
            raise ValueError(
                "Invalid or expired verification token."
            )

        # --------------------------------------
        # Mark email verified
        # --------------------------------------

        user.is_verified = True

        # --------------------------------------
        # Consume token
        # --------------------------------------

        verification_token.used = True

        # --------------------------------------
        # Save
        # --------------------------------------

        await self.db.commit()

