from pydantic import Field
from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Request for query endpoint"""

    question: str=Field(..., description="The question that was asked")
    include_sources: bool=Field(..., description="Whether to include source in the response")