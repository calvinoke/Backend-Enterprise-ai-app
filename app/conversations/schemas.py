from datetime import datetime
from uuid import UUID
from pydantic import BaseModel



# =========================
# Create Conversation
# =========================


class ConversationCreate(BaseModel):

    title: str



# =========================
# Response
# =========================


class ConversationResponse(BaseModel):

    id: UUID

    title: str

    provider: str

    model: str

    created_at: datetime


    class Config:

        from_attributes = True



# =========================
# Message Create
# =========================


class MessageCreate(BaseModel):

     role: str
     content: str



# =========================
# Message Response
# =========================


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


# =========================
# Chat Request
# =========================


class ChatRequest(BaseModel):

    question: str



# =========================
# Chat Response
# =========================


class ChatResponse(BaseModel):

    conversation_id: UUID

    question: str

    answer: str


    class Config:

        from_attributes = True