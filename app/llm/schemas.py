from pydantic import BaseModel, Field


# =====================================================
# LLM GENERATE REQUEST
# =====================================================

class LLMGenerateRequest(BaseModel):

    prompt: str = Field(
        ...,
        min_length=1,
        description="Prompt sent to the language model.",
    )

    system_prompt: str | None = Field(
        default=None,
        description="Optional system instruction.",
    )

    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
    )

    max_tokens: int = Field(
        default=1024,
        ge=1,
        le=8192,
    )


# =====================================================
# LLM GENERATE RESPONSE
# =====================================================

class LLMGenerateResponse(BaseModel):

    prompt: str

    response: str

    provider: str

    model: str

    temperature: float

    max_tokens: int