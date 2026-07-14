from abc import ABC, abstractmethod

#For changing different AI models eg openAI,gemini,LLAMA
class BaseAIProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        prompt: str,
    ) -> str:
        pass