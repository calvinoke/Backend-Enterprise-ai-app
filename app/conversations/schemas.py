from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.aiii.schemas import MessageRole


class ConversationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class ConversationResponse(BaseModel):
    id: UUID
    title: str
    provider: str
    model: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    tokens: int
    latency_ms: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    document_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: UUID
    question: str
    answer: str
    provider: str
    model: str

    class Config:
        from_attributes = True