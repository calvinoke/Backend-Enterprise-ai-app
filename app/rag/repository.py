from uuid import UUID
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.documents.models import Document
from .models import DocumentChunk


class DocumentChunkRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    # =====================================================
    # CREATE CHUNKS
    # =====================================================

    async def create_many(
        self,
        document_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
    ):

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Chunks and embeddings must have the same length."
            )

        objects = []

        for index, (
            content,
            embedding,
        ) in enumerate(
            zip(
                chunks,
                embeddings,
            )
        ):
            objects.append(
                DocumentChunk(
                    document_id=document_id,
                    chunk_index=index,
                    content=content,
                    embedding=embedding,
                )
            )

        self.session.add_all(objects)

        await self.session.flush()

        return objects

    # =====================================================
    # DELETE DOCUMENT CHUNKS
    # =====================================================

    async def delete_by_document(
        self,
        document_id: str,
    ):

        await self.session.execute(
            delete(DocumentChunk).where(
                DocumentChunk.document_id == document_id
            )
        )

        await self.session.flush()

    # =====================================================
    # SIMILARITY SEARCH
    # =====================================================

    async def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        document_id: str | None = None,
        user_id: UUID | None = None,
        similarity_threshold: float = 0.0,
    ) -> list[tuple[DocumentChunk, float]]:

        if not query_embedding:
            return []

        distance = (
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            )
        )

        similarity = 1.0 - distance

        # -------------------------------------------------
        # BASE QUERY
        # -------------------------------------------------

        query = (
            select(
                DocumentChunk,
                similarity.label("similarity"),
            )
            .join(
                Document,
                Document.id == DocumentChunk.document_id,
            )
            .where(
                DocumentChunk.embedding.is_not(None)
            )
        )

        # -------------------------------------------------
        # DOCUMENT OWNERSHIP
        # -------------------------------------------------

        if user_id is not None:
            query = query.where(
                Document.uploaded_by == user_id
            )

        # -------------------------------------------------
        # SPECIFIC DOCUMENT
        # -------------------------------------------------

        if document_id is not None:
            query = query.where(
                DocumentChunk.document_id == document_id
            )

        # -------------------------------------------------
        # SIMILARITY THRESHOLD
        # -------------------------------------------------

        if similarity_threshold > 0:
            query = query.where(
                similarity >= similarity_threshold
            )

        # -------------------------------------------------
        # ORDER + LIMIT
        # -------------------------------------------------

        query = (
            query
            .order_by(distance)
            .limit(top_k)
        )

        result = await self.session.execute(
            query
        )

        rows = result.all()

        return [
            (
                chunk,
                float(score),
            )
            for chunk, score in rows
        ]