from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_class import Base
from app.database.mixins import UUIDMixin, TimestampMixin
from app.users.enums import UserRole


if TYPE_CHECKING:
    from app.auth.models import (
        EmailVerificationToken,
        PasswordResetToken,
        RefreshToken,
    )
    from app.conversations.models import Conversation
    from app.documents.models import Document


class User(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    Application user model.

    Stores user identity, authentication state, role,
    and relationships to application resources.
    """

    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'admin')",
            name="ck_users_role",
        ),
    )

    # ========================================================
    # FIRST NAME
    # ========================================================

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # ========================================================
    # LAST NAME
    # ========================================================

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # ========================================================
    # EMAIL
    # ========================================================

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    # ========================================================
    # PASSWORD HASH
    # ========================================================

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ========================================================
    # ROLE
    # ========================================================

    role: Mapped[str] = mapped_column(
        String(50),
        default=UserRole.USER.value,
        nullable=False,
    )

    # ========================================================
    # ACTIVE STATUS
    # ========================================================

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # ========================================================
    # EMAIL VERIFICATION
    # ========================================================

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ========================================================
    # REFRESH TOKENS
    # ========================================================

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # ========================================================
    # PASSWORD RESET TOKENS
    # ========================================================

    password_reset_tokens: Mapped[
        list["PasswordResetToken"]
    ] = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # ========================================================
    # EMAIL VERIFICATION TOKENS
    # ========================================================

    email_verification_tokens: Mapped[
        list["EmailVerificationToken"]
    ] = relationship(
        "EmailVerificationToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # ========================================================
    # CONVERSATIONS
    # ========================================================

    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # ========================================================
    # DOCUMENTS
    # ========================================================

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="user",
        cascade="all, delete-orphan",
    )