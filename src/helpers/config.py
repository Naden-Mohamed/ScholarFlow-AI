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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

def get_settings():
    return Settings()