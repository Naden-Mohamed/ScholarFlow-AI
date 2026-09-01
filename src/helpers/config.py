import os

from pydantic_settings import BaseSettings

# Used to validate and manage application settings, such as API keys and configuration parameters.


class Settings(BaseSettings):
    app_name: str = "ScholarFlow AI"
    gemini_api_key: str = ""

    FILE_ALLOWED_TYPES: list[str] = []
    FILE_MAX_SIZE_MB: int = 10
    FILE_DEFAULT_CHUNK_SIZE: int = 512000  # 512 KB

    MONGODB_URI: str = ""
    MONGODB_DB_NAME: str = ""
    COLLECTION_NAME: str = ""

    POSTGRES_USERNAME: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_HOST: str = "pgvector"
    POSTGRES_PORT: int = 5432
    POSTGRES_MAIN_DATABASE: str = "scholarflow"

    GROQ_API_KEY: str = ""

    GENERATION_BACKEND: str | None = None
    EMBEDDING_BACKEND: str | None = None
    GENERATION_MODEL_ID: str | None = None
    EMBEDDING_MODEL_ID: str | None = None
    EMBEDDING_MODEL_SIZE: int | None = None
    INPUT_DEFAULT_MAX_CHARACTERS: int | None = None
    GENERATION_DEFAULT_MAX_TOKENS: int | None = None
    GENERATION_DEFAULT_TEMPERATURE: float | None = None
    TOKENIZER_MODEL_ID: str = ""

    VECTOR_DB_BACKEND_LITERAL: list[str] = []
    VECTOR_DB_BACKEND: str | None = None
    VECTOR_DB_NAME: str | None = None
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    VECTOR_DB_DISTANCE_METRIC: str | None = None
    VECTOR_DB_PGVEC_INDEX_THRESHOLD: int = 100
    TEST_SET_PATH: str = "C:/Users/start/OneDrive/Desktop/ScholarFlow AI/src/evaluation/testset/qa_pairs.json"

    PRIMARY_LANG: str = "en"
    DEFAULT_LANG: str = "en"

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        env_file_encoding = "utf-8"


def get_settings():
    return Settings()
