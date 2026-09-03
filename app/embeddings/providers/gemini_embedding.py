from google import genai
from app.core.config import settings
from ..base import EmbeddingProvider


class GeminiEmbeddingProvider(
    EmbeddingProvider
):

    def __init__(self):

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = (
            settings.EMBEDDING_MODEL
            or "text-embedding-004"
        )

        self._dimension = (
            settings.VECTOR_DIMENSION
        )

    @property
    def provider_name(self) -> str:
        return "gemini"

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

        try:

            response = await (
                self.client.aio.models.embed_content(
                    model=self.model,
                    contents=text,
                )
            )

            embedding = (
                response.embeddings[0].values
            )

            return [
                float(value)
                for value in embedding
            ]

        except Exception as exc:

            raise RuntimeError(
                f"Gemini embedding failed: {exc}"
            ) from exc

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        try:

            response = await (
                self.client.aio.models.embed_content(
                    model=self.model,
                    contents=texts,
                )
            )

            return [
                [
                    float(value)
                    for value in embedding.values
                ]
                for embedding
                in response.embeddings
            ]

        except Exception as exc:

            raise RuntimeError(
                f"Gemini batch embedding failed: {exc}"
            ) from exc