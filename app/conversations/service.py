from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.aiii.schemas import (
    AIMessage,
    MessageRole,
)

from app.aiii.service import AIService
from app.conversations.models import (
    Conversation,
    Message,
)
from app.conversations.repository import (
    ConversationRepository,
)
from app.core.config import settings
from app.prompts.manager import PromptManager



class ConversationService:


    def __init__(
        self,
        db: AsyncSession,
    ):

        self.repo = ConversationRepository(db)

        # Provider will be created dynamically
        # based on conversation provider/model
        self.ai_service = None



    # ------------------------------------
    # Create Conversation
    # ------------------------------------

    async def create_conversation(
        self,
        user_id: UUID,
        title: str,
    ):


        conversation = Conversation(

            user_id=user_id,

            title=title,

            provider=settings.AI_PROVIDER,

            model=settings.AI_MODEL,

        )


        return await self.repo.create_conversation(
            conversation
        )



    # ------------------------------------
    # List User Conversations
    # ------------------------------------

    async def get_user_conversations(
        self,
        user_id: UUID,
    ):


        return await self.repo.list_conversations(
            user_id
        )



    # ------------------------------------
    # Get Conversation
    # ------------------------------------

    async def get_conversation(
        self,
        conversation_id: UUID,
    ):


        return await self.repo.get_conversation(
            conversation_id
        )



    # ------------------------------------
    # Delete Conversation
    # ------------------------------------

    async def delete_conversation(
        self,
        conversation_id: UUID,
    ):


        conversation = await self.repo.get_conversation(
            conversation_id
        )


        if not conversation:

            raise ValueError(
                "Conversation not found"
            )


        await self.repo.delete_conversation(
            conversation
        )



    # ------------------------------------
    # Add Message
    # ------------------------------------

    async def add_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
    ):


        message = Message(

            conversation_id=conversation_id,

            role=role,

            content=content,

        )


        return await self.repo.create_message(
            message
        )



    # ------------------------------------
    # Get Messages
    # ------------------------------------

    async def get_messages(
        self,
        conversation_id: UUID,
    ):


        return await self.repo.list_messages(
            conversation_id
        )



    # ------------------------------------
    # Chat With AI
    # ------------------------------------

    async def chat(
        self,
        conversation_id: UUID,
        question: str,
    ):


        conversation = await self.repo.get_conversation(
            conversation_id
        )


        if not conversation:

            raise ValueError(
                "Conversation not found"
            )



        # --------------------------------
        # Save user question
        # --------------------------------

        await self.add_message(

            conversation_id=conversation_id,

            role=MessageRole.USER.value,

            content=question,

        )



        # --------------------------------
        # Load conversation history
        # --------------------------------

        history = await self.repo.list_messages(
            conversation_id
        )



        # --------------------------------
        # Build AI message list
        # --------------------------------

        messages: list[AIMessage] = []



        # System Prompt

        messages.append(

            AIMessage(

                role=MessageRole.SYSTEM,

                content=PromptManager.get_prompt(
                    "default"
                ),

            )

        )



        # Existing conversation history

        for message in history:


            messages.append(

                AIMessage(

                    role=MessageRole(message.role),

                    content=message.content,

                )

            )



        # --------------------------------
        # Initialize correct AI provider
        # --------------------------------

        self.ai_service = AIService(

            provider=conversation.provider,

            model=conversation.model,

        )



        # --------------------------------
        # Send to AI provider
        # --------------------------------

        answer = await self.ai_service.ask(
            messages
        )



        # --------------------------------
        # Save assistant response
        # --------------------------------

        await self.add_message(

            conversation_id=conversation_id,

            role=MessageRole.ASSISTANT.value,

            content=answer,

        )



        # --------------------------------
        # Return response
        # --------------------------------

        return {

            "conversation_id": conversation_id,

            "provider": conversation.provider,

            "model": conversation.model,

            "question": question,

            "answer": answer,

        }