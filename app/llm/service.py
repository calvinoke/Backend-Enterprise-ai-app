from groq import AsyncGroq
from app.core.config import settings


class LLMService:

    def __init__(self):

        if settings.AI_PROVIDER.lower() != "groq":
            raise ValueError(
                f"Unsupported LLM provider: "
                f"{settings.AI_PROVIDER}"
            )

        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = AsyncGroq(
            api_key=settings.GROQ_API_KEY
        )

        self.provider = settings.AI_PROVIDER

        self.model = settings.AI_MODEL

    # =====================================================
    # GENERATE
    # =====================================================

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:

        prompt = prompt.strip()

        if not prompt:
            raise ValueError(
                "Prompt cannot be empty."
            )

        messages = []

        # -------------------------------------------------
        # SYSTEM MESSAGE
        # -------------------------------------------------

        if system_prompt:

            system_prompt = system_prompt.strip()

            if system_prompt:

                messages.append(
                    {
                        "role": "system",
                        "content": system_prompt,
                    }
                )

        # -------------------------------------------------
        # USER MESSAGE
        # -------------------------------------------------

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        # -------------------------------------------------
        # GROQ REQUEST
        # -------------------------------------------------

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # -------------------------------------------------
        # EXTRACT RESPONSE
        # -------------------------------------------------

        if not response.choices:

            raise RuntimeError(
                "LLM returned no choices."
            )

        message = response.choices[0].message

        content = message.content

        if not content:

            raise RuntimeError(
                "LLM returned an empty response."
            )

        return content.strip()