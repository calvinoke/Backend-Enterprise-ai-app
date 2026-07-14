from openai import AsyncOpenAI

from app.core.config import settings
from app.aiii.providers.base import BaseAIProvider



class OpenAIProvider(BaseAIProvider):

    def __init__(self):

        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY
        )

        self.model = settings.AI_MODEL



    async def generate(
        self,
        prompt: str,
    ) -> str:


        response = await self.client.chat.completions.create(

            model=self.model,

            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ],

        )


        return response.choices[0].message.content