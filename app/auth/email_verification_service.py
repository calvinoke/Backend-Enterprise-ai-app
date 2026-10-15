
from datetime import datetime, timedelta, timezone
import os
from urllib.parse import quote

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.email_verification_repository import (
    EmailVerificationRepository,
)
from app.auth.models import EmailVerificationToken
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


# ============================================================
# CONFIGURATION
# ============================================================

EMAIL_VERIFICATION_EXPIRY_HOURS = 24


class EmailVerificationService:
    """
    Handles email verification and resend operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

        self.repository = EmailVerificationRepository(db)
        self.user_repository = UserRepository(db)

    # ========================================================
    # SEND VERIFICATION
    # ========================================================

    async def send_verification(self, email: str) -> None:
        """
        Create and send a new email verification token.

        Unknown email addresses and already-verified accounts
        are handled without revealing account existence.
        """

        email = email.strip().lower()

        # ----------------------------------------------------
        # Find user
        # ----------------------------------------------------

        user = await self.user_repository.get_by_email(email)

        if not user:
            return

        if user.is_verified:
            return

        # ----------------------------------------------------
        # Invalidate previous tokens
        # ----------------------------------------------------

        await self.repository.invalidate_user_tokens(user.id)

        # ----------------------------------------------------
        # Generate raw token
        # ----------------------------------------------------

        raw_token = generate_email_verification_token()

        # ----------------------------------------------------
        # Hash token before storing
        # ----------------------------------------------------

        token_hash = hash_email_verification_token(raw_token)

        # ----------------------------------------------------
        # Set expiration
        # ----------------------------------------------------

        now = datetime.now(timezone.utc)

        expires_at = now + timedelta(
            hours=EMAIL_VERIFICATION_EXPIRY_HOURS
        )

        # ----------------------------------------------------
        # Store hashed token
        # ----------------------------------------------------

        verification_token = EmailVerificationToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            used=False,
        )

        await self.repository.create(verification_token)
        await self.db.commit()

        # ----------------------------------------------------
        # Build frontend verification URL
        # ----------------------------------------------------

        frontend_url = os.getenv(
            "FRONTEND_URL",
            "http://localhost:5173",
        ).rstrip("/")

        verification_link = (
            f"{frontend_url}/verify-email"
            f"?token={quote(raw_token)}"
        )

        # ----------------------------------------------------
        # Send verification email using Resend
        # ----------------------------------------------------

        try:
            await send_email_verification_email(
                to_email=user.email,
                verification_link=verification_link,
                expires_hours=EMAIL_VERIFICATION_EXPIRY_HOURS,
            )

        except Exception:
            # Do not silently report email delivery as successful.
            # Log the exception and allow the API to handle failure.
            import logging

            logging.getLogger(__name__).exception(
                "Failed to send verification email."
            )
            raise

    # ========================================================
    # VERIFY EMAIL
    # ========================================================

    async def verify_email(
        self,
        data: VerifyEmailRequest,
    ) -> None:
        """
        Verify a user's email using a valid token.
        """

        # ----------------------------------------------------
        # Hash submitted token
        # ----------------------------------------------------

        token_hash = hash_email_verification_token(data.token)

        # ----------------------------------------------------
        # Current time
        # ----------------------------------------------------

        now = datetime.now(timezone.utc)

        # ----------------------------------------------------
        # Find valid token
        # ----------------------------------------------------

        verification_token = (
            await self.repository.get_valid_token(
                token_hash=token_hash,
                current_time=now,
            )
        )

        if not verification_token:
            raise ValueError(
                "Invalid or expired verification token."
            )

        # ----------------------------------------------------
        # Find user
        # ----------------------------------------------------

        user = await self.repository.get_user(
            verification_token.user_id
        )

        if not user:
            raise ValueError(
                "Invalid or expired verification token."
            )

        # ----------------------------------------------------
        # Mark email as verified
        # ----------------------------------------------------

        user.is_verified = True
        verification_token.used = True

        # ----------------------------------------------------
        # Save changes
        # ----------------------------------------------------

        await self.db.commit()

    # ========================================================
    # RESEND VERIFICATION
    # ========================================================

    async def resend_verification(
        self,
        data: ResendVerificationRequest,
    ) -> None:
        """
        Resend an email verification message.
        """

        await self.send_verification(str(data.email))
