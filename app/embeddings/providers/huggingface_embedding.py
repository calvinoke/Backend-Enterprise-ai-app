import asyncio
import logging
from huggingface_hub import InferenceClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class HuggingFaceEmbeddingProvider:
    """
    Generate text embeddings through Hugging Face Inference Providers.

    This implementation does not download or load the model locally.
    It preserves the interface required by EmbeddingService.
    """

    provider_name = "huggingface"

    def __init__(self) -> None:
        self.model_name = settings.EMBEDDING_MODEL
        self.dimension = settings.VECTOR_DIMENSION

        token = settings.HUGGINGFACE_API_KEY

        if not token:
            raise ValueError(
                "HUGGINGFACE_API_KEY is required for "
                "hosted Hugging Face embeddings."
            )

        self.client = InferenceClient(
            model=self.model_name,
            token=token,
            provider="hf-inference",
        )

        logger.info(
            "Hugging Face hosted embeddings configured: "
            "model=%s dimension=%s",
            self.model_name,
            self.dimension,
        )

    def _embed_sync(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Call the hosted embedding API synchronously."""

        response = self.client.feature_extraction(
            texts,
            normalize=True,
        )

        # Hugging Face may return an array-like response.
        if hasattr(response, "tolist"):
            response = response.tolist()

        # Normalize the result to a list of vectors.
        response = list(response)

        if not response:
            raise ValueError(
                "Hugging Face returned no embeddings."
            )

        # A single input can be returned as a flat vector.
        if isinstance(response[0], (int, float)):
            response = [response]

        if len(response) != len(texts):
            raise ValueError(
                "Embedding count mismatch: "
                f"expected {len(texts)}, got {len(response)}."
            )

        embeddings: list[list[float]] = []

        for index, vector in enumerate(response):
            if hasattr(vector, "tolist"):
                vector = vector.tolist()

            vector = [float(value) for value in vector]

            if len(vector) != self.dimension:
                raise ValueError(
                    f"Embedding {index} has dimension "
                    f"{len(vector)}; expected {self.dimension}."
                )

            embeddings.append(vector)

        return embeddings

    async def embed(self, text: str) -> list[float]:
        """Generate one embedding without blocking the event loop."""

        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                "Text must be a non-empty string."
            )

        results = await asyncio.to_thread(
            self._embed_sync,
            [text.strip()],
        )

        return results[0]

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""

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
            text.strip() for text in texts
        ]

        return await asyncio.to_thread(
            self._embed_sync,
            cleaned_texts,
        )