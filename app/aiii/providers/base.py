from abc import ABC, abstractmethod
from app.aiii.schemas import AIMessage


class BaseAIProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        messages: list[AIMessage],
    ) -> str:
        pass