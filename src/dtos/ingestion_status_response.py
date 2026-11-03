from pydantic import Field
from pydantic import BaseModel

class IngestionStatusResponse(BaseModel):
    """DTO for Ingestion status response"""

    workflow_id: str=Field(..., description="The id of workflow that has started")
    batch_id: str=Field(..., description="The id of batch that has started")
    files_total: int=Field(..., description="The total number of files that were uploaded")
    file_names: list[str]=Field(..., description="The name of files that were uploaded")
    message: str=Field(..., description="The message returned by the ingestion service")