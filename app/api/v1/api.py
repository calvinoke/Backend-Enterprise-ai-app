from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.aiii.router import router as ai_router
from app.conversations.router import router as conversation_router
from app.documents.router import router as documents_router
from app.embeddings.router import router as embeddings_router
from app.rag.router import router as rag_router
from app.llm.router import router as llm_router

api_router = APIRouter()


# ==========================
# Authentication
# ==========================

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)


# ==========================
# Users
# ==========================

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["Users"],
)


# ==========================
# AI
# ==========================

api_router.include_router(
    ai_router,
    prefix="/ai",
    tags=["AI"],
)


# ==========================
# Conversations
# ==========================

api_router.include_router(
    conversation_router,
    prefix="/conversations",
    tags=["Conversations"],
)


# ==========================
# Documents
# ==========================

api_router.include_router(
    documents_router,
)


# ==========================
# Embeddings
# ==========================

api_router.include_router(
    embeddings_router,
)


# ==========================
# RAG
# ==========================

api_router.include_router(
    rag_router,
)



api_router.include_router(
    llm_router,
)