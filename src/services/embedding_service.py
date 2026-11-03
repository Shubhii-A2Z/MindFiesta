from src.utils.logger import get_logger
from functools import lru_cache
from configs.settings import get_settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

logger=get_logger(__name__)

@lru_cache
def get_embeddings()->GoogleGenerativeAIEmbeddings:
    """Get embeddings for the application"""

    settings=get_settings()
    logger.info(f"Initializing Embeddings model: {settings.embedding_model}")

    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.google_api_key,
    )