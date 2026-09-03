from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.embeddings.service import EmbeddingService
from app.llm.service import LLMService
from .repository import DocumentChunkRepository


class RAGService:

    def __init__(
        self,
        session: AsyncSession,
    ):

        self.session = session

        self.embedding_service = (
            EmbeddingService()
        )

        self.llm_service = (
            LLMService()
        )

        self.repository = (
            DocumentChunkRepository(
                session
            )
        )

    # =====================================================
    # SEARCH
    # =====================================================

    async def search(
        self,
        query: str,
        top_k: int = 5,
        document_id: str | None = None,
        similarity_threshold: float = 0.5,
    ):

        query = query.strip()

        if not query:

            raise ValueError(
                "Search query cannot be empty."
            )

        # -------------------------------------------------
        # 1. Generate query embedding
        # -------------------------------------------------

        query_embedding = (
            await self.embedding_service
            .generate_embedding(
                query
            )
        )

        # -------------------------------------------------
        # 2. Search pgvector
        # -------------------------------------------------

        results = (
            await self.repository
            .similarity_search(
                query_embedding=query_embedding,
                top_k=top_k,
                document_id=document_id,
                similarity_threshold=(
                    similarity_threshold
                ),
            )
        )

        return results

    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    def build_context(
        self,
        results,
    ) -> str:

        if not results:

            return ""

        context_parts = []

        for index, (
            chunk,
            similarity,
        ) in enumerate(
            results,
            start=1,
        ):

            context_parts.append(
                (
                    f"[Source {index}]\n"
                    f"Document ID: "
                    f"{chunk.document_id}\n"
                    f"Chunk: "
                    f"{chunk.chunk_index}\n"
                    f"Similarity: "
                    f"{similarity:.4f}\n\n"
                    f"{chunk.content}"
                )
            )

        return "\n\n".join(
            context_parts
        )

    # =====================================================
    # BUILD SOURCES
    # =====================================================

    def build_sources(
        self,
        results,
    ):

        sources = []

        for chunk, similarity in results:

            sources.append(
                {
                    "chunk_id": str(
                        chunk.id
                    ),
                    "document_id": str(
                        chunk.document_id
                    ),
                    "chunk_index": (
                        chunk.chunk_index
                    ),
                    "content": chunk.content,
                    "similarity": round(
                        float(similarity),
                        6,
                    ),
                }
            )

        return sources

    # =====================================================
    # RETRIEVE CONTEXT
    # =====================================================

    async def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        document_id: str | None = None,
        similarity_threshold: float = 0.5,
    ):

        results = await self.search(
            query=query,
            top_k=top_k,
            document_id=document_id,
            similarity_threshold=(
                similarity_threshold
            ),
        )

        context = self.build_context(
            results
        )

        sources = self.build_sources(
            results
        )

        return (
            results,
            context,
            sources,
        )

    # =====================================================
    # GENERATE GROUNDED ANSWER
    # =====================================================

    async def answer(
        self,
        query: str,
        top_k: int = 5,
        document_id: str | None = None,
        similarity_threshold: float = 0.5,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ):

        query = query.strip()

        if not query:

            raise ValueError(
                "Question cannot be empty."
            )

        # -------------------------------------------------
        # 1. Retrieve relevant documents
        # -------------------------------------------------

        results, context, sources = (
            await self.retrieve_context(
                query=query,
                top_k=top_k,
                document_id=document_id,
                similarity_threshold=(
                    similarity_threshold
                ),
            )
        )

        # -------------------------------------------------
        # 2. No relevant information
        # -------------------------------------------------

        if not results:

            return {
                "answer": (
                    "I could not find "
                    "relevant information "
                    "in the provided documents "
                    "to answer this question."
                ),
                "sources": [],
                "source_count": 0,
                "provider": (
                    settings.AI_PROVIDER
                ),
                "model": settings.AI_MODEL,
            }

        # -------------------------------------------------
        # 3. System instruction
        # -------------------------------------------------

        system_prompt = """
You are an enterprise knowledge assistant.

Answer the user's question using ONLY the
information contained in the provided context.

Do not invent facts.

Do not use outside knowledge.

If the context does not contain enough information
to answer the question, clearly say that the
information is not available in the provided
documents.

When possible, synthesize information from
multiple sources.

Keep the answer clear, accurate and concise.
""".strip()

        # -------------------------------------------------
        # 4. Build grounded prompt
        # -------------------------------------------------

        prompt = f"""
Context:

{context}

User Question:

{query}

Instructions:

Answer the user question using only the context
above.

Do not mention information that is not supported
by the context.

If the context is insufficient, say so explicitly.
""".strip()

        # -------------------------------------------------
        # 5. Generate LLM answer
        # -------------------------------------------------

        answer = await self.llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # -------------------------------------------------
        # 6. Return answer + sources
        # -------------------------------------------------

        return {
            "answer": answer,
            "sources": sources,
            "source_count": len(
                sources
            ),
            "provider": (
                settings.AI_PROVIDER
            ),
            "model": settings.AI_MODEL,
        }