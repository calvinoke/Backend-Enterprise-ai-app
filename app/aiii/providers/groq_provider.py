from groq import AsyncGroq

from app.core.config import settings
from app.aiii.providers.base import BaseAIProvider
from app.aiii.schemas import AIMessage



class GroqProvider(BaseAIProvider):


    def __init__(
        self,
        model: str | None = None,
    ):


        self.client = AsyncGroq(

            api_key=settings.GROQ_API_KEY

        )


        self.model = (

            model

            or settings.AI_MODEL

        )



    async def generate(
        self,
        messages: list[AIMessage],
    ) -> str:


        response = await self.client.chat.completions.create(


            model=self.model,


            messages=[

                {

                    "role": (
                        message.role.value
                        if hasattr(message.role, "value")
                        else message.role
                    ),

                    "content": message.content,

                }

                for message in messages

            ],

        )


        return response.choices[0].message.content