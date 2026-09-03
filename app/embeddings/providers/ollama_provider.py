import logging
import httpx
from app.core.config import settings
from ..base import EmbeddingProvider

logger = logging.getLogger(__name__)


class OllamaEmbeddingProvider(
    EmbeddingProvider
):

    def __init__(self):

        self.base_url = (
            settings.OLLAMA_BASE_URL.rstrip("/")
        )

        self.model = (
            settings.EMBEDDING_MODEL
        )

        self._dimension = (
            settings.VECTOR_DIMENSION
        )

        self.timeout = httpx.Timeout(
            120.0,
            connect=10.0,
        )

    @property
    def provider_name(self) -> str:
        return "ollama"

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

            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:

                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.model,
                        "prompt": text,
                    },
                )

                response.raise_for_status()

                data = response.json()

                embedding = data.get(
                    "embedding"
                )

                if not embedding:
                    raise ValueError(
                        "Ollama returned no embedding."
                    )

                return [
                    float(value)
                    for value in embedding
                ]

        except httpx.ConnectError as exc:

            raise RuntimeError(
                "Cannot connect to Ollama at "
                f"{self.base_url}. "
                "Make sure Ollama is running."
            ) from exc

        except httpx.TimeoutException as exc:

            raise RuntimeError(
                f"Ollama request timed out for "
                f"model '{self.model}'."
            ) from exc

        except Exception as exc:

            logger.exception(
                "Ollama embedding failed"
            )

            raise RuntimeError(
                f"Ollama embedding failed: {exc}"
            ) from exc

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        # Ollama's embedding endpoint is called
        # once per text here.
        #
        # This keeps ordering deterministic and
        # works with the API currently being used.

        results = []

        for text in texts:

            embedding = await self.embed(
                text
            )

            results.append(embedding)

        return results