from app.database.base_class import Base

# ============================================================
# AUTHENTICATION
# ============================================================

from app.users.models import User

from app.auth.models import (
    RefreshToken,
    PasswordResetToken,
    EmailVerificationToken,
)


# ============================================================
# CONVERSATIONS
# ============================================================

from app.conversations.models import (
    Conversation,
    Message,
)


# ============================================================
# DOCUMENTS
# ============================================================

from app.documents.models import (
    Document,
    DocumentType,
    DocumentStatus,
)


# ============================================================
# RAG
# ============================================================

from app.rag.models import (
    DocumentChunk,
)


# ============================================================
# EXPORTED MODELS
# ============================================================

__all__ = [
    "Base",

    # Authentication
    "User",
    "RefreshToken",
    "PasswordResetToken",
    "EmailVerificationToken",

    # Conversations
    "Conversation",
    "Message",

    # Documents
    "Document",
    "DocumentType",
    "DocumentStatus",

    # RAG
    "DocumentChunk",
]