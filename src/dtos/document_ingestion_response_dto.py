from pydantic import Field
from pydantic import BaseModel

class DocumentIngestionResponseDTO(BaseModel):
    """DTO for document ingestion response"""

    chunks_created: str=Field(..., description="The number of chunks created")
    files: list[dict]=Field(..., description="Files that were uploaded and indexed")
    total_files: int=Field(..., description="The number of files uploaded")
    message: str=Field(..., description="The message returned by the ingestion service")