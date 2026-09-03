from enum import Enum
from pydantic import BaseModel


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class AIMessage(BaseModel):
    role: MessageRole
    content: str


class AIRequest(BaseModel):
    question: str


class AIResponse(BaseModel):
    answer: str