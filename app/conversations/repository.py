from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.conversations.models import (
    Conversation,
    Message,
)


class ConversationRepository:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    # ------------------------------------
    # Conversations
    # ------------------------------------

    async def create_conversation(
        self,
        conversation: Conversation,
    ) -> Conversation:

        self.db.add(conversation)

        await self.db.commit()

        await self.db.refresh(conversation)

        return conversation

    async def get_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID | None = None,
    ) -> Conversation | None:

        query = select(Conversation).where(
            Conversation.id == conversation_id
        )

        if user_id is not None:
            query = query.where(
                Conversation.user_id == user_id
            )

        result = await self.db.execute(query)

        return result.scalar_one_or_none()


    async def list_conversations(
        self,
        user_id: UUID,
    ) -> list[Conversation]:

        result = await self.db.execute(
            select(Conversation)
            .where(
                Conversation.user_id == user_id
            )
            .order_by(
                Conversation.created_at.desc()
            )
        )

        return result.scalars().all()


    async def delete_conversation(
        self,
        conversation: Conversation,
    ):

        await self.db.delete(conversation)

        await self.db.commit()

    # ------------------------------------
    # Messages
    # ------------------------------------

    async def create_message(
        self,
        message: Message,
    ) -> Message:

        self.db.add(message)

        await self.db.commit()

        await self.db.refresh(message)

        return message


    async def list_messages(
        self,
        conversation_id: UUID,
    ) -> list[Message]:

        result = await self.db.execute(
            select(Message)
            .where(
                Message.conversation_id
                == conversation_id
            )
            .order_by(
                Message.created_at.asc()
            )
        )

        return result.scalars().all()