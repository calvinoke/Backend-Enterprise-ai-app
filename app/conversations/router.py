from uuid import UUID
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.conversations.schemas import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    ChatRequest,
    ChatResponse,
)

from app.conversations.service import (
    ConversationService,
)

from app.conversations.dependencies import (
    get_conversation_service,
)


router = APIRouter()


# --------------------------------------------------
# Create Conversation
# --------------------------------------------------

@router.post(
    "/",
    response_model=ConversationResponse,
)
async def create_conversation(
    data: ConversationCreate,
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    try:

        return await service.create_conversation(
            user_id=user.id,
            title=data.title,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


# --------------------------------------------------
# List Conversations
# --------------------------------------------------

@router.get(
    "/",
    response_model=list[ConversationResponse],
)
async def list_conversations(
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    return await service.get_user_conversations(
        user.id
    )


# --------------------------------------------------
# Get Conversation
# --------------------------------------------------

@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
async def get_conversation(
    conversation_id: UUID,
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    try:

        return await service.get_conversation(
            conversation_id=conversation_id,
            user_id=user.id,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


# --------------------------------------------------
# Get Messages
# --------------------------------------------------

@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
async def get_messages(
    conversation_id: UUID,
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    try:

        return await service.get_messages(
            conversation_id=conversation_id,
            user_id=user.id,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


# --------------------------------------------------
# Add User Message
# --------------------------------------------------

@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
)
async def add_message(
    conversation_id: UUID,
    data: MessageCreate,
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    try:

        return await service.add_message(
            conversation_id=conversation_id,
            user_id=user.id,
            content=data.content,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


# --------------------------------------------------
# Delete Conversation
# --------------------------------------------------

@router.delete(
    "/{conversation_id}",
)
async def delete_conversation(
    conversation_id: UUID,
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    try:

        await service.delete_conversation(
            conversation_id=conversation_id,
            user_id=user.id,
        )

        return {
            "message": "Conversation deleted successfully."
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


# --------------------------------------------------
# Chat with AI
# --------------------------------------------------

@router.post(
    "/{conversation_id}/chat",
    response_model=ChatResponse,
)
async def chat(
    conversation_id: UUID,
    data: ChatRequest,
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    try:

        return await service.chat(
            conversation_id=conversation_id,
            user_id=user.id,
            question=data.question,
            document_id=data.document_id,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the chat request.",
        )