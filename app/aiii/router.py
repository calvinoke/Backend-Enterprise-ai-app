from fastapi import APIRouter, Depends

from app.aiii.schemas import (
    AIRequest,
    AIResponse,
)

from app.aiii.service import AIService
from app.aiii.dependencies import get_ai_service



router = APIRouter()



@router.post(
    "/ask",
    response_model=AIResponse,
)
async def ask_ai(
    data: AIRequest,
    service: AIService = Depends(
        get_ai_service
    ),
):

    return await service.ask(
        data.question
    )