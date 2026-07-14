from app.aiii.factory import ProviderFactory



class AIService:


    def __init__(self):

        self.provider = ProviderFactory.get_provider()



    async def ask(
        self,
        question: str,
    ):


        answer = await self.provider.generate(
            question
        )


        return {
            "question": question,
            "answer": answer,
        }