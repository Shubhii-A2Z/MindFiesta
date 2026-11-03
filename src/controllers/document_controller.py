from src.dtos.ingestion_status_response import IngestionStatusResponse
from src.dtos.async_ingestion_started_response import AsyncIngestionStartedResponse
from src.utils.temporal_helper import use_temporal
from src.dtos.document_ingestion_response_dto import DocumentIngestionResponseDTO
from src.services.ingestion_service import IngestionService
from http import HTTPStatus
from fastapi import HTTPException
from configs.settings import get_settings
from fastapi import File
from fastapi import UploadFile
from fastapi import APIRouter
from src.utils.logger import get_logger

logger=get_logger(__name__)

router=APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", summary="Upload documents for indexing")
async def upload_documents(files: list[UploadFile]=File(...,description="The files to upload")):
    settings=get_settings()

    if not files:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="No files provided")
    
    if len(files)>settings.max_files_per_upload:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Maximum {settings.max_files_per_upload} files can be uploaded at once")
    
    # Converting Uploaded documents into list of (file_name, file_content) tuples
    file_pairs: list[tuple[str, bytes]]=[]

    for file in files:
        if not file.filename:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="File has no filename.")
        content=await file.read()
        if not content:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"File {file.filename} is empty.")
        file_pairs.append((file.filename, content))
    
    # Starting temporal driven async ingestion process if temporal is enabled
    if use_temporal():

        # Importing the temporal ingestion service only if temporal is enabled
        from src.services.temporal_ingestion_service import TemporalIngestionService

        temporal_service=TemporalIngestionService()

        try:
            result=await temporal_service.start_batch_ingestion(file_pairs=file_pairs)
        except Exception as e:
            logger.error(f"Error starting temporal ingestion: {e}")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))
        
        return AsyncIngestionStartedResponse(
            workflow_id=result.get("workflow_id"),
            batch_id=result.get("batch_id"),
            files_total=result.get("files_total"),
            filenames=result.get("filenames"),
            message=result.get("message")
        )
    
    # Fallbacking to synchronous ingestion method
    service=IngestionService()

    try:
        payload=service.ingest_file_sync(file_pairs=file_pairs)
    except ValueError as e:
        logger.error(f"Error ingesting files: {e}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected Error ingesting files: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))
    
    return DocumentIngestionResponseDTO(
        chunks_created=payload.get("chunks_created"),
        files=payload.get("files"),
        total_files=payload.get("total_files"),
        message=payload.get("message")
    )


@router.get(
    "/ingestion/{workflow_id}",
    response_model=IngestionStatusResponse,
    summary="Get the status of asynchronous ingestion workflow"
)
async def get_ingestion_status(workflow_id: str)->IngestionStatusResponse:
    """Get status of asynchronous ingestion workflow"""

    if not use_temporal():
        raise HTTPException(
            status_code=HTTPStatus.NOT_ACCEPTABLE,
            detail="Asynchronous Temporal ingestion is not enabled."
        )
    
    from src.services.temporal_ingestion_service import TemporalIngestionService

    temporal_service=TemporalIngestionService()

    try:
        result=await temporal_service.get_ingestion_status(workflow_id=workflow_id)
    except Exception as e:
        logger.error(f"Error getting ingestion status: {e}")
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))
    
    return IngestionStatusResponse(
        workflow_id=workflow_id,
        batch_id=result.get("batch_id"),
        status=result.get("status"),
        files_total=result.get("files_total"),
        message=result.get("message")
    )