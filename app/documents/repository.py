from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Document


class DocumentRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def create(
        self,
        document: Document,
    ) -> Document:

        self.db.add(document)

        await self.db.commit()

        await self.db.refresh(
            document
        )

        return document

    async def get(
        self,
        document_id: UUID,
        user_id: UUID | None = None,
    ) -> Document | None:

        query = select(Document).where(
            Document.id == document_id
        )

        if user_id is not None:
            query = query.where(
                Document.uploaded_by == user_id
            )

        result = await self.db.execute(
            query
        )

        return result.scalar_one_or_none()

    async def list(
        self,
        user_id: UUID | None = None,
    ) -> list[Document]:

        query = select(Document)

        if user_id is not None:
            query = query.where(
                Document.uploaded_by == user_id
            )

        query = query.order_by(
            Document.created_at.desc()
        )

        result = await self.db.execute(
            query
        )

        return list(
            result.scalars().all()
        )

    async def update(
        self,
        document: Document,
    ) -> Document:

        await self.db.commit()

        await self.db.refresh(
            document
        )

        return document

    async def delete(
        self,
        document: Document,
    ) -> None:

        await self.db.delete(
            document
        )

        await self.db.commit()