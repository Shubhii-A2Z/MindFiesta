import os

def use_temporal()->bool:
    """Helper to tell the controller whether to use temporal driven ingestion."""
    
    return os.getenv("USE_TEMPORAL_INGESTION", "false").lower() in ("true", "1", "yes")