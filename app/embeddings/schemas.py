from pydantic import BaseModel, Field


class EmbeddingRequest(BaseModel):

    text: str = Field(
        ...,
        min_length=1,
        description="Text to embed.",
    )


class EmbeddingResponse(BaseModel):

    provider: str
    model: str
    dimension: int
    embedding: list[float]


class BatchEmbeddingRequest(BaseModel):

    texts: list[str] = Field(
        ...,
        min_length=1,
        max_length=100,
    )


class BatchEmbeddingResponse(BaseModel):

    provider: str
    model: str
    dimension: int
    embeddings: list[list[float]]


class SimilarityRequest(BaseModel):

    text1: str = Field(
        ...,
        min_length=1,
    )

    text2: str = Field(
        ...,
        min_length=1,
    )


class SimilarityResponse(BaseModel):

    text1: str
    text2: str
    similarity_score: float

    provider: str
    model: str


# =========================================================
# BATCH SIMILARITY
# =========================================================


class SimilarityPair(BaseModel):

    text1: str = Field(
        ...,
        min_length=1,
    )

    text2: str = Field(
        ...,
        min_length=1,
    )


class BatchSimilarityRequest(BaseModel):

    pairs: list[SimilarityPair] = Field(
        ...,
        min_length=1,
        max_length=100,
    )


class BatchSimilarityResult(BaseModel):

    text1: str
    text2: str
    similarity_score: float


class BatchSimilarityResponse(BaseModel):

    results: list[BatchSimilarityResult]

    provider: str
    model: str


# =========================================================
# SEMANTIC SEARCH
# =========================================================


class EmbeddingSearchRequest(BaseModel):

    query: str = Field(
        ...,
        min_length=1,
        description="Natural-language semantic search query.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of results to return.",
    )

    document_id: str | None = Field(
        default=None,
        description="Optional document ID to restrict the search.",
    )

    similarity_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum cosine similarity score.",
    )


class EmbeddingSearchResult(BaseModel):

    chunk_id: str
    document_id: str
    chunk_index: int
    content: str
    similarity: float


class EmbeddingSearchResponse(BaseModel):

    query: str

    provider: str
    model: str
    dimension: int

    results: list[EmbeddingSearchResult]

    count: int


# =========================================================
# SERVICE INFORMATION
# =========================================================


class EmbeddingErrorResponse(BaseModel):

    detail: str


class EmbeddingInfoResponse(BaseModel):

    service: str
    provider: str
    model: str
    dimension: int
    initialized: bool
    cache: dict