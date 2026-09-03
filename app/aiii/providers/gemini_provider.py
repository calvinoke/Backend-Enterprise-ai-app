from google import genai

from app.core.config import settings
from app.aiii.providers.base import BaseAIProvider
from app.aiii.schemas import AIMessage


class GeminiProvider(BaseAIProvider):


    def __init__(
        self,
        model: str | None = None,
    ):

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

        self.model = (
            model
            or settings.AI_MODEL
        )


    async def generate(
        self,
        messages: list[AIMessage],
    ) -> str:


        contents = []


        for message in messages:


            contents.append(

                {
                    "role": message.role.value
                    if hasattr(message.role, "value")
                    else message.role,

                    "parts": [
                        {
                            "text": message.content
                        }
                    ],
                }

            )


        response = await self.client.aio.models.generate_content(

            model=self.model,

            contents=contents,

        )


        return response.text