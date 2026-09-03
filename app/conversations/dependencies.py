from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db

from app.conversations.service import ConversationService


def get_conversation_service(
    db: AsyncSession = Depends(get_db),
):

    return ConversationService(db)