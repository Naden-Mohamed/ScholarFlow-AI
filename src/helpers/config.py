from pydantic_settings import BaseSettings, SettingsConfigDict
# Used to validate and manage application settings, such as API keys and configuration parameters.

class Settings(BaseSettings):
    app_name: str = "ScholarFlow AI"
    gemini_api_key: str = ""

    FILE_ALLOWED_TYPES: list[str]
    FILE_MAX_SIZE_MB: int = 10
    FILE_DEFAULT_CHUNK_SIZE: int = 512000 # 512 KB

    MONGODB_URI: str
    MONGODB_DB_NAME: str

    GROQ_API_KEY: str


    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None
    INPUT_DEFAULT_MAX_CHARACTERS: int = None
    GENERATION_DEFAULT_MAX_TOKENS: int = None
    GENERATION_DEFAULT_TEMPERATURE: float = None

    VECTOR_DB_URL: str = None
    VECTOR_DB_API_KEY: str = None
    VECTOR_DB_DISTANCE_METRIC: str = None
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

def get_settings():
    return Settings()