from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Application
    APP_NAME: str = "Enterprise AI Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    API_V1_PREFIX: str = "/api/v1"

    HOST: str = "0.0.0.0"
    PORT: int = 8000


    # Database

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    DATABASE_URL: str


    # Security

    SECRET_KEY: str

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


    # Redis

    REDIS_HOST: str = "localhost"

    REDIS_PORT: int = 6379

    REDIS_DB: int = 0



    # ==========================
    # AI PROVIDERS
    # ==========================


    AI_PROVIDER: str = "groq"

    AI_MODEL: str = "llama-3.1-8b-instant"


    # OpenAI

    OPENAI_API_KEY: str | None = None


    # Google Gemini

    GEMINI_API_KEY: str | None = None


    # Groq

    GROQ_API_KEY: str | None = None



    # Embeddings

    EMBEDDING_MODEL: str = "text-embedding-3-small"


    VECTOR_DIMENSION: int = 1536



    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )



@lru_cache
def get_settings():

    return Settings()



settings = get_settings()