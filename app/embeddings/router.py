import logging
import time

import numpy as np

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.database.session import get_db
from app.rag.service import RAGService
from app.users.models import User

from .schemas import (
    BatchEmbeddingRequest,
    BatchEmbeddingResponse,
    BatchSimilarityRequest,
    BatchSimilarityResponse,
    BatchSimilarityResult,
    EmbeddingInfoResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingSearchRequest,
    EmbeddingSearchResponse,
    EmbeddingSearchResult,
    SimilarityRequest,
    SimilarityResponse,
)

from .service import EmbeddingService


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/embeddings",
    tags=["Embeddings"],
)

embedding_service = EmbeddingService()


# =========================================================
# COSINE SIMILARITY - NUMPY ONLY
# =========================================================

def cosine_similarity(a, b):
    """
    Calculate pairwise cosine similarity between rows
    of two embedding matrices.

    Returns a matrix shaped (number of rows in a,
    number of rows in b), matching the shape returned
    by sklearn.metrics.pairwise.cosine_similarity.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    if a.ndim == 1:
        a = a.reshape(1, -1)

    if b.ndim == 1:
        b = b.reshape(1, -1)

    if a.ndim != 2 or b.ndim != 2:
        raise ValueError("Embeddings must be one- or two-dimensional.")

    if a.shape[1] != b.shape[1]:
        raise ValueError("Embedding vectors must have matching dimensions.")

    if a.shape[1] == 0:
        raise ValueError("Embedding vectors cannot be empty.")

    a_norm = np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = np.linalg.norm(b, axis=1, keepdims=True)

    denominator = a_norm @ b_norm.T

    # A zero vector has undefined cosine similarity.
    # Return zero for those comparisons rather than NaN.
    denominator = np.where(denominator == 0, 1.0, denominator)

    scores = (a @ b.T) / denominator

    return np.clip(scores, -1.0, 1.0)


# =========================================================
# GENERATE SINGLE EMBEDDING
# ADMIN ONLY
# =========================================================

@router.post(
    "/generate",
    response_model=EmbeddingResponse,
)
async def generate_embedding(
    request: EmbeddingRequest,
    _admin: User = Depends(require_admin),
):
    try:
        embedding = await embedding_service.generate_embedding(
            request.text
        )

        return EmbeddingResponse(
            provider=embedding_service.provider_name,
            model=embedding_service.model_name,
            dimension=len(embedding),
            embedding=embedding,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Embedding generation failed")

        raise HTTPException(
            status_code=500,
            detail="Embedding generation failed.",
        ) from exc


# =========================================================
# GENERATE BATCH EMBEDDINGS
# ADMIN ONLY
# =========================================================

@router.post(
    "/generate-batch",
    response_model=BatchEmbeddingResponse,
)
async def generate_batch_embeddings(
    request: BatchEmbeddingRequest,
    _admin: User = Depends(require_admin),
):
    try:
        embeddings = await embedding_service.generate_embeddings(
            request.texts
        )

        return BatchEmbeddingResponse(
            provider=embedding_service.provider_name,
            model=embedding_service.model_name,
            dimension=len(embeddings[0]) if embeddings else 0,
            embeddings=embeddings,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Batch embedding generation failed")

        raise HTTPException(
            status_code=500,
            detail="Batch embedding generation failed.",
        ) from exc


# =========================================================
# CALCULATE SIMILARITY
# ADMIN ONLY
# =========================================================

@router.post(
    "/similarity",
    response_model=SimilarityResponse,
)
async def calculate_similarity(
    request: SimilarityRequest,
    _admin: User = Depends(require_admin),
):
    try:
        start = time.perf_counter()

        embeddings = await embedding_service.generate_embeddings(
            [
                request.text1,
                request.text2,
            ]
        )

        if len(embeddings) != 2:
            raise ValueError(
                "Expected two embeddings for similarity calculation."
            )

        vec1 = np.asarray(embeddings[0], dtype=np.float64).reshape(1, -1)
        vec2 = np.asarray(embeddings[1], dtype=np.float64).reshape(1, -1)

        score = float(cosine_similarity(vec1, vec2)[0, 0])

        elapsed = (time.perf_counter() - start) * 1000

        logger.info(
            "Similarity calculated in %.2fms: %.6f",
            elapsed,
            score,
        )

        return SimilarityResponse(
            text1=request.text1,
            text2=request.text2,
            similarity_score=score,
            provider=embedding_service.provider_name,
            model=embedding_service.model_name,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Similarity calculation failed")

        raise HTTPException(
            status_code=500,
            detail="Similarity calculation failed.",
        ) from exc


# =========================================================
# CALCULATE BATCH SIMILARITY
# ADMIN ONLY
# =========================================================

@router.post(
    "/similarity/batch",
    response_model=BatchSimilarityResponse,
)
async def calculate_batch_similarity(
    request: BatchSimilarityRequest,
    _admin: User = Depends(require_admin),
):
    try:
        start = time.perf_counter()

        texts = []

        for pair in request.pairs:
            texts.append(pair.text1)
            texts.append(pair.text2)

        embeddings = await embedding_service.generate_embeddings(
            texts
        )

        if len(embeddings) != len(texts):
            raise ValueError(
                "The embedding service returned an unexpected number "
                "of embeddings."
            )

        results = []

        for index, pair in enumerate(request.pairs):
            vec1 = np.asarray(
                embeddings[index * 2],
                dtype=np.float64,
            ).reshape(1, -1)

            vec2 = np.asarray(
                embeddings[index * 2 + 1],
                dtype=np.float64,
            ).reshape(1, -1)

            score = float(cosine_similarity(vec1, vec2)[0, 0])

            results.append(
                BatchSimilarityResult(
                    text1=pair.text1,
                    text2=pair.text2,
                    similarity_score=score,
                )
            )

        elapsed = (time.perf_counter() - start) * 1000

        logger.info(
            "Batch similarity calculated: pairs=%s elapsed=%.2fms",
            len(request.pairs),
            elapsed,
        )

        return BatchSimilarityResponse(
            results=results,
            provider=embedding_service.provider_name,
            model=embedding_service.model_name,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Batch similarity calculation failed")

        raise HTTPException(
            status_code=500,
            detail="Batch similarity calculation failed.",
        ) from exc


# =========================================================
# SEMANTIC SEARCH
# ADMIN ONLY
#
# Normal users should use POST /rag/search.
# =========================================================

@router.post(
    "/search",
    response_model=EmbeddingSearchResponse,
)
async def semantic_search(
    request: EmbeddingSearchRequest,
    _admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    try:
        start = time.perf_counter()

        service = RAGService(db)

        results = await service.search(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
            similarity_threshold=request.similarity_threshold,
        )

        response_results = []

        for chunk, similarity in results:
            response_results.append(
                EmbeddingSearchResult(
                    chunk_id=str(chunk.id),
                    document_id=str(chunk.document_id),
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    similarity=round(similarity, 6),
                )
            )

        elapsed = (time.perf_counter() - start) * 1000

        logger.info(
            "Embedding semantic search completed: "
            "results=%s top_k=%s threshold=%.3f elapsed=%.2fms",
            len(response_results),
            request.top_k,
            request.similarity_threshold,
            elapsed,
        )

        return EmbeddingSearchResponse(
            query=request.query.strip(),
            provider=embedding_service.provider_name,
            model=embedding_service.model_name,
            dimension=embedding_service.dimension,
            results=response_results,
            count=len(response_results),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Embedding semantic search failed")

        raise HTTPException(
            status_code=500,
            detail="Semantic search failed.",
        ) from exc


# =========================================================
# HEALTH CHECK
# =========================================================

@router.get("/health")
async def health_check():
    try:
        embedding = await embedding_service.generate_embedding(
            "health check",
            use_cache=False,
        )

        return {
            "status": "healthy",
            "provider": embedding_service.provider_name,
            "model": embedding_service.model_name,
            "dimension": len(embedding),
            "initialized": embedding_service.is_initialized,
        }

    except Exception as exc:
        logger.exception("Embedding health check failed")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Embedding service is unavailable.",
        ) from exc


# =========================================================
# SERVICE INFORMATION
# ADMIN ONLY
# =========================================================

@router.get(
    "/info",
    response_model=EmbeddingInfoResponse,
)
async def service_info(
    _admin: User = Depends(require_admin),
):
    return EmbeddingInfoResponse(
        service="Embedding Service",
        provider=embedding_service.provider_name,
        model=embedding_service.model_name,
        dimension=embedding_service.dimension,
        initialized=embedding_service.is_initialized,
        cache=embedding_service.get_cache_stats(),
    )
