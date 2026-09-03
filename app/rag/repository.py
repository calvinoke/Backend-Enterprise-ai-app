from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import DocumentChunk


class DocumentChunkRepository:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    # =====================================================
    # CREATE MANY
    # =====================================================

    async def create_many(
        self,
        document_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
    ):
        if len(chunks) != len(embeddings):
            raise ValueError(
                "Chunks and embeddings must have "
                "the same length."
            )

        objects = []

        for index, (
            content,
            embedding,
        ) in enumerate(
            zip(chunks, embeddings)
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
        similarity_threshold: float = 0.0,
    ) -> list[
        tuple[DocumentChunk, float]
    ]:

        if not query_embedding:
            return []

        # -------------------------------------------------
        # Calculate cosine distance
        # -------------------------------------------------

        distance = (
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            )
        )

        # -------------------------------------------------
        # Convert cosine distance to similarity
        # -------------------------------------------------

        similarity = 1.0 - distance

        # -------------------------------------------------
        # Build similarity search query
        # -------------------------------------------------

        query = (
            select(
                DocumentChunk,
                similarity.label("similarity"),
            )
            .where(
                DocumentChunk.embedding.is_not(None)
            )
            .order_by(distance)
            .limit(top_k)
        )

        # -------------------------------------------------
        # Optional document filter
        # -------------------------------------------------

        if document_id:
            query = query.where(
                DocumentChunk.document_id == document_id
            )

        # -------------------------------------------------
        # Optional similarity threshold
        # -------------------------------------------------

        if similarity_threshold > 0:
            query = query.where(
                similarity >= similarity_threshold
            )

        # -------------------------------------------------
        # Execute query
        # -------------------------------------------------

        result = await self.session.execute(query)

        rows = result.all()

        # -------------------------------------------------
        # Return chunks and similarity scores
        # -------------------------------------------------

        return [
            (
                chunk,
                float(score),
            )
            for chunk, score in rows
        ]