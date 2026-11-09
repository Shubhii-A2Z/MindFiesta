from pydantic import Field
from pydantic import BaseModel

class SourceDocument(BaseModel):
    """Source document"""

    content: str=Field(..., description="The content of document")
    metadata: dict=Field(..., description="The metadata of document")


class QueryRequest(BaseModel):
    """Request for query endpoint"""

    question: str=Field(..., description="The question that was asked")
    include_sources: bool=Field(..., description="Whether to include source in the response")


class QueryResponse(BaseModel):
    """Response for query endpoint"""

    question: str=Field(..., description="The question that was asked")
    answer: str=Field(..., description="The answer to the query")
    source: list[SourceDocument]=Field(..., description="The source of the answer")
    processing_time_ms: float=Field(..., description="Processing time in milliseconds")