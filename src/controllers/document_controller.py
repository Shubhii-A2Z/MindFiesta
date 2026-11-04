from src.controllers.strategies.ingestion_strategy import IngestionResponse
from src.controllers.factories.ingestion_strategy_factory import IngestionStrategyFactory
from src.dtos.ingestion_status_response import IngestionStatusResponse
from src.utils.temporal_helper import use_temporal
from http import HTTPStatus
from fastapi import HTTPException
from configs.settings import get_settings
from fastapi import File
from fastapi import UploadFile
from fastapi import APIRouter
from src.utils.logger import get_logger

logger=get_logger(__name__)

router=APIRouter(prefix="/documents", tags=["documents"])

@router.post(
    "/upload",
    response_model=IngestionResponse,
    summary="Upload documents for indexing"
)
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

    try:
        ingestion_strategy=IngestionStrategyFactory.get_ingestion_strategy()
        return await ingestion_strategy.execute(file_pairs=file_pairs)
    except Exception as e:
        logger.error(f"Unexpected error ingestion files: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


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
    
    return IngestionStatusResponse(**result)