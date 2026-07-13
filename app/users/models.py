from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_class import Base
from app.database.mixins import UUIDMixin, TimestampMixin

class User(
    Base,
    UUIDMixin,
    TimestampMixin,
):

    __tablename__ = "users"


    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )


    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    role: Mapped[str] = mapped_column(
        String(50),
        default="user",
        nullable=False,
    )


    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )


    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete",
    )