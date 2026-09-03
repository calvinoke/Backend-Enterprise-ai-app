from app.core.config import settings


class ProviderFactory:


    @staticmethod
    def get_provider(
        provider: str | None = None,
        model: str | None = None,
    ):


        provider = (
            provider 
            or settings.AI_PROVIDER
        ).lower()


        print(
            "====== AI PROVIDER SELECTED ======",
            provider
        )


        if provider == "groq":

            from app.aiii.providers.groq_provider import GroqProvider

            return GroqProvider(
                model=model
            )


        elif provider == "gemini":

            from app.aiii.providers.gemini_provider import GeminiProvider

            return GeminiProvider(
                model=model
            )


        elif provider == "openai":

            from app.aiii.providers.openai_provider import OpenAIProvider

            return OpenAIProvider(
                model=model
            )


        raise ValueError(
            f"Unsupported provider {provider}"
        )