from urllib3.util import url
from configs.settings import get_settings
from qdrant_client import QdrantClient

def get_qdrant_client()->QdrantClient:
    """Create the QDrant Client for the application"""
    
    settings=get_settings()
    return QdrantClient(
        url=settings.qdrant_url,
    )