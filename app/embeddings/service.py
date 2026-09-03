import logging
import time
from typing import Any
from app.core.config import settings
from .factory import EmbeddingFactory

logger = logging.getLogger(__name__)


class EmbeddingService:

    def __init__(self):

        self.provider = EmbeddingFactory.get_provider()

        self.provider_name = (
            self.provider.provider_name
        )

        self.model_name = (
            self.provider.model_name
        )

        self.vector_dimension = (
            self.provider.dimension
        )

        self._initialized = True

        self._cache: dict[str, list[float]] = {}

        self._cache_hits = 0
        self._cache_misses = 0

        logger.info(
            "EmbeddingService initialized: "
            "provider=%s model=%s dimension=%s",
            self.provider_name,
            self.model_name,
            self.vector_dimension,
        )

    # =====================================================
    # SINGLE EMBEDDING
    # =====================================================

    async def generate_embedding(
        self,
        text: str,
        use_cache: bool = True,
    ) -> list[float]:

        text = self._validate_text(text)

        if use_cache and text in self._cache:

            self._cache_hits += 1

            return self._cache[text]

        self._cache_misses += 1

        start = time.perf_counter()

        embedding = await self.provider.embed(text)

        self._validate_dimension(embedding)

        if use_cache:
            self._cache[text] = embedding

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        logger.debug(
            "Embedding generated in %.2fms",
            elapsed,
        )

        return embedding

    # =====================================================
    # BATCH EMBEDDINGS
    # =====================================================

    async def generate_embeddings(
        self,
        texts: list[str],
        use_cache: bool = True,
    ) -> list[list[float]]:

        if not texts:
            return []

        validated_texts = [
            self._validate_text(text)
            for text in texts
        ]

        results: list[list[float] | None] = [
            None
            for _ in validated_texts
        ]

        texts_to_embed: list[str] = []
        indexes_to_embed: list[int] = []

        # -----------------------------------------------
        # Resolve cache while preserving original order
        # -----------------------------------------------

        for index, text in enumerate(
            validated_texts
        ):

            if (
                use_cache
                and text in self._cache
            ):

                self._cache_hits += 1

                results[index] = (
                    self._cache[text]
                )

            else:

                self._cache_misses += 1

                texts_to_embed.append(text)

                indexes_to_embed.append(index)

        # -----------------------------------------------
        # Generate missing embeddings
        # -----------------------------------------------

        if texts_to_embed:

            new_embeddings = (
                await self.provider.embed_batch(
                    texts_to_embed
                )
            )

            if len(new_embeddings) != len(
                texts_to_embed
            ):
                raise ValueError(
                    "Embedding provider returned "
                    f"{len(new_embeddings)} embeddings "
                    f"for {len(texts_to_embed)} texts."
                )

            for (
                index,
                text,
                embedding,
            ) in zip(
                indexes_to_embed,
                texts_to_embed,
                new_embeddings,
            ):

                self._validate_dimension(
                    embedding
                )

                results[index] = embedding

                if use_cache:
                    self._cache[text] = embedding

        # -----------------------------------------------
        # Safety check
        # -----------------------------------------------

        final_results = []

        for result in results:

            if result is None:
                raise RuntimeError(
                    "Failed to generate embedding."
                )

            final_results.append(result)

        return final_results

    async def generate_batch_embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        return await self.generate_embeddings(
            texts
        )

    # =====================================================
    # VALIDATION
    # =====================================================

    @staticmethod
    def _validate_text(
        text: str,
    ) -> str:

        if not isinstance(text, str):
            raise ValueError(
                "Text must be a string."
            )

        text = text.strip()

        if not text:
            raise ValueError(
                "Text cannot be empty."
            )

        return text

    def _validate_dimension(
        self,
        embedding: list[float],
    ):

        actual = len(embedding)

        expected = self.vector_dimension

        if actual != expected:

            raise ValueError(
                "Embedding dimension mismatch. "
                f"Expected {expected}, got {actual}. "
                f"Provider={self.provider_name}, "
                f"model={self.model_name}"
            )

    # =====================================================
    # CACHE
    # =====================================================

    def clear_cache(self):

        size = len(self._cache)

        self._cache.clear()

        self._cache_hits = 0
        self._cache_misses = 0

        logger.info(
            "Embedding cache cleared: %s entries",
            size,
        )

    def get_cache_stats(
        self,
    ) -> dict[str, Any]:

        total = (
            self._cache_hits
            + self._cache_misses
        )

        return {
            "cache_size": len(self._cache),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_ratio": (
                self._cache_hits / total
                if total
                else 0
            ),
        }

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def dimension(self) -> int:
        return self.vector_dimension

    @property
    def provider_type(self) -> str:
        return self.provider_name

    @property
    def model(self) -> str:
        return self.model_name

    @property
    def is_initialized(self) -> bool:
        return self._initialized