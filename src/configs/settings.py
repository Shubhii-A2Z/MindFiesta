from functools import lru_cache
from pydantic_settings import SettingsConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Env settings for the application
    Automatically reads configurations from environment variables and validate them at runtime.
    """

    # Loading the configs from .env file
    model_config=SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Groq related configs
    google_api_key: str=""

    # Qdrant related configs
    qdrant_url: str=""

    # Temporal related configs
    temporal_host: str=""
    temporal_namespace: str=""
    temporal_task_queue: str=""

    # Collection and LLM Models related configs
    collection_name: str=""
    embedding_model: str=""
    llm_model: str=""
    llm_temperature: float=0.0
    chunk_size: int=1000
    chunk_overlap: int=200
    retrieval_k: int=4

    # API related configs
    api_host: str="0.0.0.0"
    api_port: int=8000
    log_level: str="INFO"
    app_name: str="YoutubeTranscriptRAG"

    # Upload limits
    max_files_per_upload: int=10
    index_batch_size: int=100

    # Ingestion mode
    # Async temporal ingestion. In case if temporal is down -> ingest using sync process
    use_temporal_ingestion: bool=False

    # RAGAS (evaluation related configs)
    enable_ragas_evaluation: bool=False


@lru_cache
def get_settings()->Settings:
    return Settings()