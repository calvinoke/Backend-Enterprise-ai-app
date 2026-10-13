from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.auth.dependencies import (
    require_admin,
)

from app.core.config import settings
from app.users.models import User
from .schemas import (
    LLMGenerateRequest,
    LLMGenerateResponse,
)
from .service import LLMService


router = APIRouter(
    prefix="/llm",
    tags=["LLM"],
)


# =========================================================
# GENERATE
# ADMIN ONLY
#
# Normal users access the LLM indirectly through
# /rag/answer and the Chat functionality.
# =========================================================

@router.post(
    "/generate",
    response_model=LLMGenerateResponse,
)
async def generate(
    request: LLMGenerateRequest,
    _admin: User = Depends(
        require_admin
    ),
):

    try:

        service = LLMService()

        response = await service.generate(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return LLMGenerateResponse(
            prompt=request.prompt,
            response=response,
            provider=settings.AI_PROVIDER,
            model=settings.AI_MODEL,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc