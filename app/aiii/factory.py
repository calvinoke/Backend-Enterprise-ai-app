from app.core.config import settings

from app.aiii.providers.openai_provider import OpenAIProvider
from app.aiii.providers.gemini_provider import GeminiProvider
from app.aiii.providers.groq_provider import GroqProvider



class ProviderFactory:


    @staticmethod
    def get_provider():


        provider = settings.AI_PROVIDER.lower()



        if provider == "openai":

            return OpenAIProvider()



        elif provider == "gemini":

            return GeminiProvider()



        elif provider == "groq":

            return GroqProvider()



        else:

            raise ValueError(
                f"Unsupported AI provider: {provider}"
            )