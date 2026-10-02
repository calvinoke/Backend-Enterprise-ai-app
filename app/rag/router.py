from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.config import settings
from app.database.session import get_db
from app.users.models import User

from .schemas import (
    RAGAnswerRequest,
    RAGAnswerResponse,
    RAGContextRequest,
    RAGContextResponse,
    RAGSearchRequest,
    RAGSearchResponse,
    RAGSearchResult,
    RAGSource,
)
from .service import RAGService


router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)


# =========================================================
# SEMANTIC SEARCH
# =========================================================

@router.post(
    "/search",
    response_model=RAGSearchResponse,
)
async def search_documents(
    request: RAGSearchRequest,
    user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):

    try:

        service = RAGService(db)

        results = await service.search(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
            user_id=user.id,
            similarity_threshold=(
                request.similarity_threshold
            ),
        )

        response_results = []

        for chunk, similarity in results:

            response_results.append(
                RAGSearchResult(
                    chunk_id=str(
                        chunk.id
                    ),
                    document_id=str(
                        chunk.document_id
                    ),
                    chunk_index=(
                        chunk.chunk_index
                    ),
                    content=chunk.content,
                    similarity=round(
                        float(similarity),
                        6,
                    ),
                )
            )

        return RAGSearchResponse(
            query=request.query,
            provider=(
                settings.EMBEDDING_PROVIDER
            ),
            model=(
                settings.EMBEDDING_MODEL
            ),
            dimension=(
                settings.VECTOR_DIMENSION
            ),
            results=response_results,
            count=len(
                response_results
            ),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to perform "
                "document search."
            ),
        )


# =========================================================
# RETRIEVE CONTEXT
# =========================================================

@router.post(
    "/context",
    response_model=RAGContextResponse,
)
async def retrieve_context(
    request: RAGContextRequest,
    user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):

    try:

        service = RAGService(db)

        (
            _results,
            context,
            sources,
        ) = await service.retrieve_context(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
            user_id=user.id,
            similarity_threshold=(
                request.similarity_threshold
            ),
        )

        response_sources = [
            RAGSearchResult(**source)
            for source in sources
        ]

        return RAGContextResponse(
            query=request.query,
            context=context,
            sources=response_sources,
            count=len(
                response_sources
            ),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve "
                "document context."
            ),
        )


# =========================================================
# RAG ANSWER
# =========================================================

@router.post(
    "/answer",
    response_model=RAGAnswerResponse,
)
async def generate_rag_answer(
    request: RAGAnswerRequest,
    user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):

    try:

        service = RAGService(db)

        result = await service.answer(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
            user_id=user.id,
            similarity_threshold=(
                request.similarity_threshold
            ),
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        response_sources = [
            RAGSource(**source)
            for source in result["sources"]
        ]

        return RAGAnswerResponse(
            query=request.query,
            answer=result["answer"],
            provider=result["provider"],
            model=result["model"],
            sources=response_sources,
            source_count=(
                result["source_count"]
            ),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to generate "
                "RAG answer."
            ),
        )