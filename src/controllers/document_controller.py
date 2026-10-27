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

