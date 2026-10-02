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
from app.rag.service import RAGService


class ConversationService:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.repo = ConversationRepository(db)

        # RAG service used for document-grounded conversations.
        self.rag_service = RAGService(db)

    # ------------------------------------
    # Create Conversation
    # ------------------------------------

    async def create_conversation(
        self,
        user_id: UUID,
        title: str,
    ):

        title = title.strip()

        if not title:
            raise ValueError(
                "Conversation title cannot be empty."
            )

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
        user_id: UUID,
    ):

        conversation = await self.repo.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if not conversation:
            raise ValueError(
                "Conversation not found."
            )

        return conversation

    # ------------------------------------
    # Delete Conversation
    # ------------------------------------

    async def delete_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ):

        conversation = await self.repo.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if not conversation:
            raise ValueError(
                "Conversation not found."
            )

        await self.repo.delete_conversation(
            conversation
        )

    # ------------------------------------
    # Add User Message
    # ------------------------------------

    async def add_message(
        self,
        conversation_id: UUID,
        user_id: UUID,
        content: str,
    ):

        # Verify conversation ownership first.
        conversation = await self.repo.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if not conversation:
            raise ValueError(
                "Conversation not found."
            )

        content = content.strip()

        if not content:
            raise ValueError(
                "Message content cannot be empty."
            )

        message = Message(
            conversation_id=conversation_id,
            role=MessageRole.USER.value,
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
        user_id: UUID,
    ):

        # Verify ownership before returning messages.
        conversation = await self.repo.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if not conversation:
            raise ValueError(
                "Conversation not found."
            )

        return await self.repo.list_messages(
            conversation_id
        )

    # ------------------------------------
    # Chat With AI
    # ------------------------------------

    async def chat(
        self,
        conversation_id: UUID,
        user_id: UUID,
        question: str,
        document_id: str | None = None,
    ):

        # --------------------------------
        # Verify conversation ownership
        # --------------------------------

        conversation = await self.repo.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if not conversation:
            raise ValueError(
                "Conversation not found."
            )

        # --------------------------------
        # Validate question
        # --------------------------------

        question = question.strip()

        if not question:
            raise ValueError(
                "Question cannot be empty."
            )

        # --------------------------------
        # Save user question
        # --------------------------------

        await self.repo.create_message(
            Message(
                conversation_id=conversation_id,
                role=MessageRole.USER.value,
                content=question,
            )
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

        # --------------------------------
        # Base system prompt
        # --------------------------------

        messages.append(
            AIMessage(
                role=MessageRole.SYSTEM,
                content=PromptManager.get_prompt(
                    "default"
                ),
            )
        )

        # --------------------------------
        # Retrieve RAG context
        # --------------------------------

        if document_id:

            _results, context, _sources = (
                await self.rag_service.retrieve_context(
                    query=question,
                    top_k=5,
                    document_id=document_id,
                    user_id=user_id,
                    similarity_threshold=0.5,
                )
            )

            # --------------------------------
            # Add retrieved context
            # --------------------------------

            if context:

                rag_prompt = f"""
You are answering a question using information
retrieved from the provided document.

Use ONLY the information contained in the
retrieved document context.

Do not invent facts.

Do not use outside knowledge.

If the retrieved context does not contain
enough information to answer the question,
clearly state that the information is not
available in the provided document.

Retrieved Document Context:

{context}
""".strip()

                messages.append(
                    AIMessage(
                        role=MessageRole.SYSTEM,
                        content=rag_prompt,
                    )
                )

            else:

                messages.append(
                    AIMessage(
                        role=MessageRole.SYSTEM,
                        content=(
                            "No relevant information was "
                            "retrieved from the provided document. "
                            "Do not use outside knowledge to answer "
                            "the user's question. If the answer is "
                            "not available in the conversation "
                            "history, clearly state that the "
                            "information is not available."
                        ),
                    )
                )

        # --------------------------------
        # Add conversation history
        # --------------------------------

        for message in history:

            try:
                role = MessageRole(message.role)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid message role stored in conversation: "
                    f"{message.role}"
                ) from exc

            messages.append(
                AIMessage(
                    role=role,
                    content=message.content,
                )
            )

        # --------------------------------
        # Initialize AI provider
        # --------------------------------

        ai_service = AIService(
            provider=conversation.provider,
            model=conversation.model,
        )

        # --------------------------------
        # Send messages to AI provider
        # --------------------------------

        answer = await ai_service.ask(
            messages
        )

        # --------------------------------
        # Save assistant response
        # --------------------------------

        await self.repo.create_message(
            Message(
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT.value,
                content=answer,
            )
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