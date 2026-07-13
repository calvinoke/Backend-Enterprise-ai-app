from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_class import Base
from app.database.mixins import UUIDMixin, TimestampMixin


class RefreshToken(
    Base,
    UUIDMixin,
    TimestampMixin,
):

    __tablename__ = "refresh_tokens"


    user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )


    token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )


    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )


    user = relationship(
        "User",
        back_populates="refresh_tokens",
        lazy="joined",
    )