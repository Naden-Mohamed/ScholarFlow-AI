from pydantic_settings import BaseSettings
from typing import List, Optional
import os  
# Used to validate and manage application settings, such as API keys and configuration parameters.

class Settings(BaseSettings):
    app_name: str = "ScholarFlow AI"
    gemini_api_key: str = ""

    FILE_ALLOWED_TYPES: List[str] = []
    FILE_MAX_SIZE_MB: int = 10
    FILE_DEFAULT_CHUNK_SIZE: int = 512000 # 512 KB

    MONGODB_URI: str = ""
    MONGODB_DB_NAME: str = ""
    COLLECTION_NAME: str = ""

    POSTGRES_USERNAME: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_MAIN_DATABASE: str = "scholarflow"

    GROQ_API_KEY: str = ""

    GENERATION_BACKEND: Optional[str] = None
    EMBEDDING_BACKEND: Optional[str] = None
    GENERATION_MODEL_ID: Optional[str] = None
    EMBEDDING_MODEL_ID: Optional[str] = None
    EMBEDDING_MODEL_SIZE: Optional[int] = None
    INPUT_DEFAULT_MAX_CHARACTERS: Optional[int] = None
    GENERATION_DEFAULT_MAX_TOKENS: Optional[int] = None
    GENERATION_DEFAULT_TEMPERATURE: Optional[float] = None
    TOKENIZER_MODEL_ID: str = ""

    VECTOR_DB_BACKEND: Optional[str] = None
    VECTOR_DB_NAME: Optional[str] = None
    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    VECTOR_DB_DISTANCE_METRIC: Optional[str] = None
    
    PRIMARY_LANG: str = "en"
    DEFAULT_LANG: str = "en"
    
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")       
        env_file_encoding = "utf-8"
def get_settings():
    return Settings()