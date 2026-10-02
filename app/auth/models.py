from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database.base_class import Base
from app.database.mixins import UUIDMixin, TimestampMixin


# ============================================================
# TYPE CHECKING IMPORTS
# ============================================================
# This prevents circular import problems at runtime while still
# allowing IDEs and type checkers to understand the User model.
# ============================================================

if TYPE_CHECKING:
    from app.users.models import User


# ============================================================
# REFRESH TOKEN
# ============================================================

class RefreshToken(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    Stores hashed refresh tokens used to obtain new access tokens.
    """

    __tablename__ = "refresh_tokens"

    # ========================================================
    # USER ID
    # ========================================================

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ========================================================
    # HASHED REFRESH TOKEN
    # ========================================================
    # We never store the original refresh token in the database.
    # Only its hash is stored.
    # ========================================================

    token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # ========================================================
    # EXPIRATION
    # ========================================================

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # ========================================================
    # REVOKED
    # ========================================================

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ========================================================
    # USER RELATIONSHIP
    # ========================================================

    user: Mapped["User"] = relationship(
        "User",
        back_populates="refresh_tokens",
        lazy="joined",
    )


# ============================================================
# PASSWORD RESET TOKEN
# ============================================================

class PasswordResetToken(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    Stores password-reset tokens.

    Only the SHA-256 hash of the reset token is stored in the
    database. The original token is sent to the user's email.
    """

    __tablename__ = "password_reset_tokens"

    # ========================================================
    # USER ID
    # ========================================================

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ========================================================
    # HASHED RESET TOKEN
    # ========================================================

    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )

    # ========================================================
    # EXPIRATION
    # ========================================================

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # ========================================================
    # SINGLE USE
    # ========================================================

    used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ========================================================
    # USER RELATIONSHIP
    # ========================================================

    user: Mapped["User"] = relationship(
        "User",
        back_populates="password_reset_tokens",
    )


# ============================================================
# EMAIL VERIFICATION TOKEN
# ============================================================

class EmailVerificationToken(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    Stores email-verification tokens.

    The raw token is sent to the user's email while only the
    SHA-256 hash is stored in the database.
    """

    __tablename__ = "email_verification_tokens"

    # ========================================================
    # USER ID
    # ========================================================

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # ========================================================
    # HASHED VERIFICATION TOKEN
    # ========================================================

    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )

    # ========================================================
    # EXPIRATION
    # ========================================================

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # ========================================================
    # SINGLE USE
    # ========================================================

    used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ========================================================
    # USER RELATIONSHIP
    # ========================================================

    user: Mapped["User"] = relationship(
        "User",
        back_populates="email_verification_tokens",
    )