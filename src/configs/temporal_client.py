from configs.settings import get_settings
from temporalio.client import Client

async def get_temporal_client()->Client:
    """Create temporal client for the application"""
    
    settings=get_settings()
    return await Client.connect(
        target_host=settings.temporal_host,
        namespace=settings.temporal_namespace
    )