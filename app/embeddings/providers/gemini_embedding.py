import asyncio
import logging

from google import genai
from google.genai import types

from app.core.config import settings
from ..base import EmbeddingProvider

logger = logging.getLogger(__name__)


class GeminiEmbeddingProvider(EmbeddingProvider):
    """
    Generate text embeddings using Google's hosted Gemini API.

    Supports:
    - Single text embeddings
    - Batch text embeddings
    - Configurable vector dimensions
    - Asynchronous execution
    - Input and output validation
    """

    # Maximum number of texts sent in one API request.
    BATCH_SIZE = 100

    def __init__(self) -> None:
        """Initialize the Gemini embedding provider."""

        if not settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is required when "
                "EMBEDDING_PROVIDER=gemini."
            )

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = settings.EMBEDDING_MODEL
        self._dimension = settings.VECTOR_DIMENSION

        logger.info(
            "Gemini embedding provider initialized: "
            "model=%s dimension=%s",
            self.model,
            self._dimension,
        )

    # =====================================================
    # PROVIDER PROPERTIES
    # =====================================================

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self.model

    @property
    def dimension(self) -> int:
        return self._dimension

    # =====================================================
    # INTERNAL SYNCHRONOUS EMBEDDING
    # =====================================================

    def _embed_sync(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings using the synchronous Gemini SDK.

        This method is executed in a worker thread by the
        asynchronous public methods.
        """

        if not texts:
            return []

        # Create a separate Content object for every input.
        # This ensures each text is embedded independently.
        contents = [
            types.Content(
                parts=[
                    types.Part.from_text(text=text)
                ]
            )
            for text in texts
        ]

        response = self.client.models.embed_content(
            model=self.model,
            contents=contents,
            config=types.EmbedContentConfig(
                output_dimensionality=self._dimension,
            ),
        )

        if not response.embeddings:
            raise ValueError(
                "Gemini returned no embeddings."
            )

        if len(response.embeddings) != len(texts):
            raise ValueError(
                f"Expected {len(texts)} embeddings, "
                f"but Gemini returned "
                f"{len(response.embeddings)}."
            )

        results: list[list[float]] = []

        for index, item in enumerate(response.embeddings):
            if item.values is None:
                raise ValueError(
                    f"Gemini returned an empty embedding "
                    f"for input index {index}."
                )

            vector = [
                float(value)
                for value in item.values
            ]

            if len(vector) != self._dimension:
                raise ValueError(
                    f"Embedding at index {index} has "
                    f"{len(vector)} dimensions; expected "
                    f"{self._dimension}. "
                    f"Model={self.model}"
                )

            results.append(vector)

        return results

    # =====================================================
    # SINGLE EMBEDDING
    # =====================================================

    async def embed(
        self,
        text: str,
    ) -> list[float]:
        """Generate an embedding for a single text."""

        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                "Text must be a non-empty string."
            )

        cleaned_text = text.strip()

        try:
            results = await asyncio.to_thread(
                self._embed_sync,
                [cleaned_text],
            )

            if len(results) != 1:
                raise ValueError(
                    "Expected exactly one embedding, "
                    f"received {len(results)}."
                )

            return results[0]

        except Exception as exc:
            logger.exception(
                "Gemini single embedding failed."
            )

            raise RuntimeError(
                f"Gemini embedding failed: {exc}"
            ) from exc

    # =====================================================
    # BATCH EMBEDDINGS
    # =====================================================

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Large input lists are divided into smaller requests.
        The returned embeddings preserve the original input
        order.
        """

        if not texts:
            return []

        if any(
            not isinstance(text, str) or not text.strip()
            for text in texts
        ):
            raise ValueError(
                "Every text must be a non-empty string."
            )

        cleaned_texts = [
            text.strip()
            for text in texts
        ]

        all_embeddings: list[list[float]] = []

        try:
            for start in range(
                0,
                len(cleaned_texts),
                self.BATCH_SIZE,
            ):
                batch = cleaned_texts[
                    start : start + self.BATCH_SIZE
                ]

                logger.debug(
                    "Generating Gemini embeddings: "
                    "batch_start=%s batch_size=%s",
                    start,
                    len(batch),
                )

                batch_embeddings = await asyncio.to_thread(
                    self._embed_sync,
                    batch,
                )

                if len(batch_embeddings) != len(batch):
                    raise ValueError(
                        f"Expected {len(batch)} embeddings, "
                        f"received {len(batch_embeddings)}."
                    )

                all_embeddings.extend(batch_embeddings)

            if len(all_embeddings) != len(cleaned_texts):
                raise ValueError(
                    f"Expected {len(cleaned_texts)} total "
                    f"embeddings, received "
                    f"{len(all_embeddings)}."
                )

            logger.info(
                "Gemini batch embedding completed: "
                "texts=%s dimensions=%s",
                len(all_embeddings),
                self._dimension,
            )

            return all_embeddings

        except Exception as exc:
            logger.exception(
                "Gemini batch embedding failed."
            )

            raise RuntimeError(
                f"Gemini batch embedding failed: {exc}"
            ) from exc
