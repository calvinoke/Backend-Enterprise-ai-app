from fastapi import APIRouter

from app.core.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

api_router = APIRouter()


def log_import_start(module_name: str) -> None:
    logger.info("router_import_start", module=module_name)


def log_import_success(module_name: str) -> None:
    logger.info("router_import_success", module=module_name)


# ==========================
# Authentication
# ==========================

log_import_start("app.auth.router")
from app.auth.router import router as auth_router
log_import_success("app.auth.router")


# ==========================
# Users
# ==========================

log_import_start("app.users.router")
from app.users.router import router as users_router
log_import_success("app.users.router")


# ==========================
# AI
# ==========================

log_import_start("app.aiii.router")
from app.aiii.router import router as ai_router
log_import_success("app.aiii.router")


# ==========================
# Conversations
# ==========================

log_import_start("app.conversations.router")
from app.conversations.router import router as conversation_router
log_import_success("app.conversations.router")


# ==========================
# Documents
# ==========================

log_import_start("app.documents.router")
from app.documents.router import router as documents_router
log_import_success("app.documents.router")


# ==========================
# Embeddings
# ==========================

log_import_start("app.embeddings.router")
from app.embeddings.router import router as embeddings_router
log_import_success("app.embeddings.router")


# ==========================
# RAG
# ==========================

log_import_start("app.rag.router")
from app.rag.router import router as rag_router
log_import_success("app.rag.router")


# ==========================
# LLM
# ==========================

log_import_start("app.llm.router")
from app.llm.router import router as llm_router
log_import_success("app.llm.router")


# ==========================
# Register routes
# ==========================

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["Users"],
)

api_router.include_router(
    ai_router,
    prefix="/ai",
    tags=["AI"],
)

api_router.include_router(
    conversation_router,
    prefix="/conversations",
    tags=["Conversations"],
)

api_router.include_router(documents_router)
api_router.include_router(embeddings_router)
api_router.include_router(rag_router)
api_router.include_router(llm_router)

logger.info("all_api_routers_registered")