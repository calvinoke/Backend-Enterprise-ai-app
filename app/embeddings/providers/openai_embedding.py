from openai import AsyncOpenAI

from app.core.config import settings
from ..base import EmbeddingProvider


class OpenAIEmbeddingProvider(
    EmbeddingProvider
):

    def __init__(self):

        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
        )

        self.model = (
            settings.EMBEDDING_MODEL
            or "text-embedding-3-small"
        )

        self._dimension = (
            settings.VECTOR_DIMENSION
        )

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self.model

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed(
        self,
        text: str,
    ) -> list[float]:

        response = await self.client.embeddings.create(
            model=self.model,
            input=text,
        )

        embedding = (
            response.data[0].embedding
        )

        return [
            float(value)
            for value in embedding
        ]

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )

        # OpenAI returns embeddings with indexes.
        ordered = sorted(
            response.data,
            key=lambda item: item.index,
        )

        return [
            [
                float(value)
                for value in item.embedding
            ]
            for item in ordered
        ]