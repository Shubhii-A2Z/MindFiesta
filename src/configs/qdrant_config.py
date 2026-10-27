from src.utils.logger import get_logger
from urllib3.util import url
from configs.settings import get_settings
from qdrant_client import QdrantClient

logger=get_logger(__name__)

def get_qdrant_client()->QdrantClient:
    """Create the QDrant Client for the application"""

    settings=get_settings()
    logger.info(f"Initializing QDrant Client with URL: {settings.qdrant_url}")
    
    return QdrantClient(
        url=settings.qdrant_url,
    )