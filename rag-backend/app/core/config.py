from pydantic_settings import BaseSettings
from typing import Optional, List
import json
import os

class Settings(BaseSettings):
    APP_NAME: str
    DEBUG: bool
    API_V1_STR: str

    DATABASE_URL: str
    DATABASE_POOL_SIZE: int
    DATABASE_MAX_OVERFLOW: int

    # Redis Configuration
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    CACHE_TTL: int

    EMBEDDING_MODEL: str
    RERANKER_MODEL: str
    MAX_TOKENS: int
    TEMPERATURE: float

    OPENAI_API_KEY: str

    MAX_DOCUMENT_SIZE: int
    SUPPORTED_FILE_TYPES: str
    CHUNKING_STRATEGY: str
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int

    TOP_K_DOCUMENTS: int
    SIMILARITY_THRESHOLD: float
    RERANKER_SCORE_THRESHOLD: float

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str

    LOG_LEVEL: str
    LOG_FORMAT: str

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def supported_file_types(self) -> List[str]:
        return json.loads(self.SUPPORTED_FILE_TYPES)

settings = Settings() 