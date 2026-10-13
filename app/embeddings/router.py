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

from sklearn.metrics.pairwise import (
    cosine_similarity,
)

from app.auth.dependencies import (
    require_admin,
)

from app.database.session import get_db

from app.rag.service import (
    RAGService,
)

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

from .service import (
    EmbeddingService,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/embeddings",
    tags=["Embeddings"],
)


embedding_service = EmbeddingService()


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
    _admin: User = Depends(
        require_admin
    ),
):
    try:
        embedding = (
            await embedding_service.generate_embedding(
                request.text
            )
        )

        return EmbeddingResponse(
            provider=(
                embedding_service.provider_name
            ),
            model=(
                embedding_service.model_name
            ),
            dimension=len(embedding),
            embedding=embedding,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        logger.exception(
            "Embedding generation failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
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
    _admin: User = Depends(
        require_admin
    ),
):
    try:
        embeddings = (
            await embedding_service.generate_embeddings(
                request.texts
            )
        )

        return BatchEmbeddingResponse(
            provider=(
                embedding_service.provider_name
            ),
            model=(
                embedding_service.model_name
            ),
            dimension=(
                len(embeddings[0])
                if embeddings
                else 0
            ),
            embeddings=embeddings,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        logger.exception(
            "Batch embedding generation failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
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
    _admin: User = Depends(
        require_admin
    ),
):
    try:
        start = time.perf_counter()

        embeddings = (
            await embedding_service.generate_embeddings(
                [
                    request.text1,
                    request.text2,
                ]
            )
        )

        vec1 = np.array(
            embeddings[0]
        ).reshape(
            1,
            -1,
        )

        vec2 = np.array(
            embeddings[1]
        ).reshape(
            1,
            -1,
        )

        score = float(
            cosine_similarity(
                vec1,
                vec2,
            )[0][0]
        )

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        logger.info(
            "Similarity calculated in %.2fms: %.6f",
            elapsed,
            score,
        )

        return SimilarityResponse(
            text1=request.text1,
            text2=request.text2,
            similarity_score=score,
            provider=(
                embedding_service.provider_name
            ),
            model=(
                embedding_service.model_name
            ),
        )

    except Exception as exc:

        logger.exception(
            "Similarity calculation failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
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
    _admin: User = Depends(
        require_admin
    ),
):
    try:
        start = time.perf_counter()

        texts = []

        for pair in request.pairs:
            texts.append(pair.text1)
            texts.append(pair.text2)

        embeddings = (
            await embedding_service.generate_embeddings(
                texts
            )
        )

        results = []

        for index, pair in enumerate(
            request.pairs
        ):
            vec1 = np.array(
                embeddings[index * 2]
            ).reshape(
                1,
                -1,
            )

            vec2 = np.array(
                embeddings[index * 2 + 1]
            ).reshape(
                1,
                -1,
            )

            score = float(
                cosine_similarity(
                    vec1,
                    vec2,
                )[0][0]
            )

            results.append(
                BatchSimilarityResult(
                    text1=pair.text1,
                    text2=pair.text2,
                    similarity_score=score,
                )
            )

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        logger.info(
            "Batch similarity calculated: "
            "pairs=%s elapsed=%.2fms",
            len(request.pairs),
            elapsed,
        )

        return BatchSimilarityResponse(
            results=results,
            provider=(
                embedding_service.provider_name
            ),
            model=(
                embedding_service.model_name
            ),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        logger.exception(
            "Batch similarity calculation failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# =========================================================
# SEMANTIC SEARCH
# ADMIN ONLY
#
# Normal users should use:
# POST /rag/search
#
# =========================================================

@router.post(
    "/search",
    response_model=EmbeddingSearchResponse,
)
async def semantic_search(
    request: EmbeddingSearchRequest,
    _admin: User = Depends(
        require_admin
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):
    try:
        start = time.perf_counter()

        service = RAGService(db)

        results = await service.search(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
            similarity_threshold=(
                request.similarity_threshold
            ),
        )

        response_results = []

        for chunk, similarity in results:

            response_results.append(
                EmbeddingSearchResult(
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
                        similarity,
                        6,
                    ),
                )
            )

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        logger.info(
            "Embedding semantic search completed: "
            "results=%s top_k=%s threshold=%.3f "
            "elapsed=%.2fms",
            len(response_results),
            request.top_k,
            request.similarity_threshold,
            elapsed,
        )

        return EmbeddingSearchResponse(
            query=request.query.strip(),
            provider=(
                embedding_service.provider_name
            ),
            model=(
                embedding_service.model_name
            ),
            dimension=(
                embedding_service.dimension
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

    except Exception as exc:

        logger.exception(
            "Embedding semantic search failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Semantic search failed.",
        ) from exc


# =========================================================
# HEALTH CHECK
#
# Kept public so infrastructure/readiness checks can
# determine whether the embedding service is available.
# =========================================================

@router.get(
    "/health",
)
async def health_check():

    try:
        embedding = (
            await embedding_service.generate_embedding(
                "health check",
                use_cache=False,
            )
        )

        return {
            "status": "healthy",
            "provider": (
                embedding_service.provider_name
            ),
            "model": (
                embedding_service.model_name
            ),
            "dimension": len(embedding),
            "initialized": (
                embedding_service.is_initialized
            ),
        }

    except Exception as exc:

        logger.exception(
            "Embedding health check failed"
        )

        raise HTTPException(
            status_code=(
                status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=str(exc),
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
    _admin: User = Depends(
        require_admin
    ),
):

    return EmbeddingInfoResponse(
        service="Embedding Service",
        provider=(
            embedding_service.provider_name
        ),
        model=(
            embedding_service.model_name
        ),
        dimension=(
            embedding_service.dimension
        ),
        initialized=(
            embedding_service.is_initialized
        ),
        cache=(
            embedding_service.get_cache_stats()
        ),
    )