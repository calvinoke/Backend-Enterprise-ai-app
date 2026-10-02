from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from .models import (
    DocumentStatus,
    DocumentType,
)


class DocumentUploadResponse(BaseModel):
    id: UUID
    filename: str
    original_filename: str
    document_type: DocumentType
    status: DocumentStatus
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    original_filename: str
    document_type: DocumentType
    status: DocumentStatus
    content: str | None
    uploaded_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True