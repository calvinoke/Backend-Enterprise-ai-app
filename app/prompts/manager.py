from .templates import SYSTEM_PROMPTS


class PromptManager:

    @staticmethod
    def get_prompt(name: str = "default") -> str:

        return SYSTEM_PROMPTS.get(
            name,
            SYSTEM_PROMPTS["default"],
        )