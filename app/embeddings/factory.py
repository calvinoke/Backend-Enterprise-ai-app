import logging

from app.core.config import settings
logger = logging.getLogger(__name__)


class EmbeddingFactory:

    _instance = None
    _provider_name = None

    @classmethod
    def get_provider(
        cls,
        provider_name: str | None = None,
    ):

        provider = (
            provider_name
            or settings.EMBEDDING_PROVIDER
        ).lower().strip()

        # Return cached provider
        if (
            cls._instance is not None
            and cls._provider_name == provider
        ):
            return cls._instance

        logger.info(
            "Creating embedding provider: %s",
            provider,
        )

        if provider == "ollama":

            from .providers.ollama_provider import (
                OllamaEmbeddingProvider,
            )

            instance = OllamaEmbeddingProvider()

        elif provider == "openai":

            from .providers.openai_embedding import (
                OpenAIEmbeddingProvider,
            )

            instance = OpenAIEmbeddingProvider()

        elif provider == "gemini":

            from .providers.gemini_embedding import (
                GeminiEmbeddingProvider,
            )

            instance = GeminiEmbeddingProvider()

        elif provider in {
            "huggingface",
            "sentence_transformers",
        }:

            from .providers.huggingface_embedding import (
                HuggingFaceEmbeddingProvider,
            )

            instance = HuggingFaceEmbeddingProvider()

        else:

            raise ValueError(
                f"Unsupported embedding provider: {provider}. "
                "Supported providers: "
                "ollama, openai, gemini, huggingface."
            )

        cls._instance = instance
        cls._provider_name = provider

        logger.info(
            "Embedding provider initialized: %s",
            instance.__class__.__name__,
        )

        logger.info(
            "Embedding model: %s",
            instance.model_name,
        )

        logger.info(
            "Embedding dimension: %s",
            instance.dimension,
        )

        return instance

    @classmethod
    def reset(cls):
        cls._instance = None
        cls._provider_name = None

    @classmethod
    def create(cls):
        return cls.get_provider()