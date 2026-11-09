from http import HTTPStatus
from fastapi.exceptions import HTTPException
from src.dtos.query_response import SourceDocument
from src.services.rag_query_service import RAGQueryService
from time import time
from src.dtos.query_request import QueryRequest
from importlib.resources import path
from src.dtos.query_response import QueryResponse
from fastapi import APIRouter
from src.utils.logger import get_logger

logger=get_logger(__name__)

router=APIRouter(
    prefix="/query"
)

@router.get(
    "/",
    summary="Query the vector store",
    response_model=QueryResponse
)
async def query(query: QueryRequest):
    
    start=time()
    rag_service=RAGQueryService()

    try:

        if query.include_sources:
            result=await rag_service.aquery_with_source(question=query.question)
            source=[SourceDocument(**doc) for doc in result["source"]]
        else:
            result=await rag_service.aquery(question=query.question)
            source=None
        processing_time_ms=time()-start

        return QueryResponse(
            question=query.question,
            answer=result.get("answer", ""),
            source=source,
            processing_time_ms=processing_time_ms
        )

    except Exception as e:
        logger.error(f"Error querying the vector store: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))