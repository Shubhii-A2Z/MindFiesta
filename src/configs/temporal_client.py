from configs.settings import get_settings
from temporalio.client import Client

async def get_temporal_client()->Client:
    """Create temporal client for the application"""
    
    settings=get_settings()
    return Client.connect(
        namespace=settings.temporal_namespace
    )