from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    # =====================================================
    # APPLICATION
    # =====================================================

    APP_NAME: str = "Enterprise AI Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    API_V1_PREFIX: str = "/api/v1"

    HOST: str = "0.0.0.0"
    PORT: int = 8000


    # =====================================================
    # DATABASE
    # =====================================================

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    DATABASE_URL: str


    # =====================================================
    # SECURITY
    # =====================================================

    SECRET_KEY: str

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


    # =====================================================
    # REDIS
    # =====================================================

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0


    # =====================================================
    # LLM PROVIDER
    # =====================================================

    AI_PROVIDER: str = "groq"

    AI_MODEL: str = "llama-3.1-8b-instant"


    # =====================================================
    # EMBEDDING PROVIDER
    # =====================================================

    EMBEDDING_PROVIDER: str = "ollama"

    EMBEDDING_MODEL: str = "nomic-embed-text"

    VECTOR_DIMENSION: int = 768


    # =====================================================
    # API KEYS
    # =====================================================

    OPENAI_API_KEY: str | None = None

    GEMINI_API_KEY: str | None = None

    GROQ_API_KEY: str | None = None

    HUGGINGFACE_API_KEY: str | None = None

    OLLAMA_BASE_URL: str = "http://localhost:11434"


    # =====================================================
    # MODEL CONFIG
    # =====================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


@lru_cache
def get_settings():

    return Settings()


settings = get_settings()