from src.dtos.async_ingestion_started_response import AsyncIngestionStartedResponse
from http import HTTPStatus
from fastapi import HTTPException
from src.utils.logger import get_logger
from src.services.temporal_ingestion_service import TemporalIngestionService
from src.controllers.strategies.ingestion_strategy import IngestionStrategy

logger=get_logger(__name__)

class TemporalIngestionStrategy(IngestionStrategy):

    def __init__(self):
        self.service=TemporalIngestionService()

    async def execute(self, file_pairs: list[tuple[str, bytes]])->AsyncIngestionStartedResponse:
        try:
            result=await self.service.start_batch_ingestion(file_pairs=file_pairs)
        except Exception as e:
            logger.error(f"Error starting temporal ingestion: {e}")
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))
        
        return AsyncIngestionStartedResponse(**result)