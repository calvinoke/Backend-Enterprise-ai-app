import google.generativeai as genai

from app.core.config import settings
from app.aiii.providers.base import BaseAIProvider



class GeminiProvider(BaseAIProvider):


    def __init__(self):

        genai.configure(
            api_key=settings.GEMINI_API_KEY
        )


        self.model = genai.GenerativeModel(
            settings.AI_MODEL
        )



    async def generate(
        self,
        prompt:str,
    )->str:


        response = await self.model.generate_content_async(
            prompt
        )


        return response.text