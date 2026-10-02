from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.core.config import settings
from app.database.base_class import Base
from app.database.mixins import (
    TimestampMixin,
    UUIDMixin,
)


class DocumentChunk(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "document_chunks"

    document_id: Mapped[str] = mapped_column(
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(settings.VECTOR_DIMENSION),
        nullable=True,
    )

    document = relationship(
        "Document",
        back_populates="chunks",
    )