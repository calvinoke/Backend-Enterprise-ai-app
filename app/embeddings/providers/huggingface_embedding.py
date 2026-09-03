from sentence_transformers import (
    SentenceTransformer,
)
from app.core.config import settings
from ..base import EmbeddingProvider


class HuggingFaceEmbeddingProvider(
    EmbeddingProvider
):

    def __init__(self):

        self.model = SentenceTransformer(
            settings.EMBEDDING_MODEL
        )

        self._dimension = (
            self.model.get_embedding_dimension()
        )

        if not self._dimension:
            raise ValueError(
                "Unable to determine "
                "HuggingFace embedding dimension."
            )

    @property
    def provider_name(self) -> str:
        return "huggingface"

    @property
    def model_name(self) -> str:
        return settings.EMBEDDING_MODEL

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed(
        self,
        text: str,
    ) -> list[float]:

        vector = self.model.encode(
            text,
            convert_to_numpy=True,
        )

        return [
            float(value)
            for value in vector.tolist()
        ]

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        vectors = self.model.encode(
            texts,
            convert_to_numpy=True,
        )

        return [
            [
                float(value)
                for value in vector.tolist()
            ]
            for vector in vectors
        ]