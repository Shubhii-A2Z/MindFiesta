from src.utils.logger import get_logger
from pathlib import Path
from src.services.strategies.document_loader_strategy import DocumentLoaderStrategy
from langchain_core.documents import Document

logger=get_logger(__name__)

class PdfLoaderStrategy(DocumentLoaderStrategy):

    def load(self, file_path: Path, source_name: str | None=None) -> list[Document]:
        """Load PDF file into list of Documents"""

        raise NotImplementedError("PDF loading is not yet implemented")
