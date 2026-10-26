from functools import lru_cache
from configs.settings import get_settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

@lru_cache
def get_embeddings()->GoogleGenerativeAIEmbeddings:
    """Get embeddings for the application"""
    settings=get_settings()

    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
    )