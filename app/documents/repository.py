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
    ):

        self.db.add(document)

        await self.db.commit()

        await self.db.refresh(
            document
        )

        return document

    async def get(
        self,
        document_id: UUID,
    ):

        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id
            )
        )

        return result.scalar_one_or_none()

    async def list(self):

        result = await self.db.execute(
            select(Document).order_by(
                Document.created_at.desc()
            )
        )

        return result.scalars().all()

    async def update(
        self,
        document: Document,
    ):

        await self.db.commit()

        await self.db.refresh(
            document
        )

        return document

    async def delete(
        self,
        document: Document,
    ):

        await self.db.delete(
            document
        )

        await self.db.commit()