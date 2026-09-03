from app.aiii.factory import ProviderFactory
from app.aiii.schemas import AIMessage


class AIService:

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
    ):

        self.provider = ProviderFactory.get_provider(
            provider=provider,
            model=model,
        )

    async def ask(
        self,
        messages: list[AIMessage],
    ) -> str:

        return await self.provider.generate(
            messages
        )
