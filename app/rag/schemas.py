from pydantic import BaseModel, Field


# =========================================================
# SEARCH
# =========================================================

class RAGSearchRequest(BaseModel):

    query: str = Field(
        ...,
        min_length=1,
        description="Natural-language query.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
    )

    document_id: str | None = None

    similarity_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )


class RAGSearchResult(BaseModel):

    chunk_id: str

    document_id: str

    chunk_index: int

    content: str

    similarity: float


class RAGSearchResponse(BaseModel):

    query: str

    provider: str

    model: str

    dimension: int

    results: list[RAGSearchResult]

    count: int


# =========================================================
# CONTEXT
# =========================================================

class RAGContextRequest(BaseModel):

    query: str = Field(
        ...,
        min_length=1,
        description="Question used to retrieve context.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
    )

    document_id: str | None = None

    similarity_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )


class RAGContextResponse(BaseModel):

    query: str

    context: str

    sources: list[RAGSearchResult]

    count: int


# =========================================================
# ANSWER
# =========================================================

class RAGAnswerRequest(BaseModel):

    query: str = Field(
        ...,
        min_length=1,
        description="Natural-language question.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    document_id: str | None = None

    similarity_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )

    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
    )

    max_tokens: int = Field(
        default=1024,
        ge=1,
        le=8192,
    )


class RAGSource(BaseModel):

    chunk_id: str

    document_id: str

    chunk_index: int

    content: str

    similarity: float


class RAGAnswerResponse(BaseModel):

    query: str

    answer: str

    provider: str

    model: str

    sources: list[RAGSource]

    source_count: int