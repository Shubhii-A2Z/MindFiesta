from src.dtos.document_ingestion_response_dto import DocumentIngestionResponseDTO
from http import HTTPStatus
from fastapi import HTTPException
from src.utils.logger import get_logger
from src.services.ingestion_service import IngestionService
from src.controllers.strategies.ingestion_strategy import IngestionStrategy

logger=get_logger(__name__)

class SynchronousIngestionStrategy(IngestionStrategy):

    def __init__(self):
        self.service=IngestionService()

    async def execute(self, file_pairs: list[tuple[str, bytes]])->DocumentIngestionResponseDTO:
        try:
            payload=self.service.ingest_file_sync(file_pairs=file_pairs)
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