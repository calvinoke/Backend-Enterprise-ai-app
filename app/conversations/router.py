from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from app.conversations.schemas import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    ChatRequest,
    ChatResponse,
)

from app.conversations.service import ConversationService
from app.conversations.dependencies import (
    get_conversation_service,
)


router = APIRouter()


# --------------------------------------------------
# Temporary user id
# Replace later with current_user from JWT
# --------------------------------------------------

TEST_USER_ID = UUID(
    "3fd77472-c21c-4ec6-a8b2-9e5b94b4f921"
)


# --------------------------------------------------
# Create Conversation
# --------------------------------------------------

@router.post(
    "/",
    response_model=ConversationResponse,
)
async def create_conversation(
    data: ConversationCreate,
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    return await service.create_conversation(
        user_id=TEST_USER_ID,
        title=data.title,
    )


# --------------------------------------------------
# List Conversations
# --------------------------------------------------

@router.get(
    "/",
    response_model=list[ConversationResponse],
)
async def list_conversations(
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    return await service.get_user_conversations(
        TEST_USER_ID
    )


# --------------------------------------------------
# Get Messages
# --------------------------------------------------

@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
async def get_messages(
    conversation_id: UUID,
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    return await service.get_messages(
        conversation_id
    )


# --------------------------------------------------
# Add Message
# --------------------------------------------------

@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
)
async def add_message(
    conversation_id: UUID,
    data: MessageCreate,
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    return await service.add_message(
        conversation_id=conversation_id,
        role=data.role,
        content=data.content,
    )


# --------------------------------------------------
# Delete Conversation
# --------------------------------------------------

@router.delete(
    "/{conversation_id}",
)
async def delete_conversation(
    conversation_id: UUID,
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    try:

        await service.delete_conversation(
            conversation_id
        )

        return {
            "message": "Conversation deleted successfully."
        }

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


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
    service: ConversationService = Depends(
        get_conversation_service
    ),
):

    try:

        return await service.chat(
            conversation_id=conversation_id,
            question=data.question,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )