from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from .service import DocumentService


def get_document_service(
    db: AsyncSession = Depends(get_db),
):

    return DocumentService(db)