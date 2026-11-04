from src.dtos.async_ingestion_started_response import AsyncIngestionStartedResponse
from src.dtos.document_ingestion_response_dto import DocumentIngestionResponseDTO
from typing import Union
from abc import abstractmethod
from abc import ABC

IngestionResponse=Union[
    DocumentIngestionResponseDTO,
    AsyncIngestionStartedResponse
]

class IngestionStrategy(ABC):

    @abstractmethod
    async def execute(self, file_pairs: list[tuple[str, bytes]])->IngestionResponse:
        pass