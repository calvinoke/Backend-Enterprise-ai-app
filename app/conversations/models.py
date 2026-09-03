from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base_class import Base
from app.database.mixins import UUIDMixin, TimestampMixin


class Conversation(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "conversations"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="New Conversation",
    )

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="conversations",
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class Message(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "messages"

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        nullable=False,
    )

    tokens: Mapped[int] = mapped_column(
        default=0,
    )

    latency_ms: Mapped[int] = mapped_column(
        default=0,
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages",
    )