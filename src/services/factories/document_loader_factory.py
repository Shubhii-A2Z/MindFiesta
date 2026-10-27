from src.services.strategies.pdf_loader_strategy import PdfLoaderStrategy
from src.services.strategies.csv_loader_strategy import CsvLoaderStrategy
from src.exceptions.unsupported_file_error import UnsupportedFileError
from src.services.strategies.document_loader_strategy import DocumentLoaderStrategy
from pathlib import Path

class DocumentLoaderFactory:
    """Factory for creating document loaders based on extension type."""

    SUPPORTED_FILE_EXTENSIONS={".csv"}

    @staticmethod
    def get_loader(file_path: Path)->DocumentLoaderStrategy:
        file_path=Path(file_path)

        # Getting the document extension type (.csv, .txt, .pdf, etc)
        file_extension=file_path.suffix.lower()

        if file_extension not in DocumentLoaderFactory.SUPPORTED_FILE_EXTENSIONS:
            raise UnsupportedFileError(f"Unsupported file type: {file_extension}")

        if file_extension==".csv":
            return CsvLoaderStrategy()
        elif file_extension==".pdf":
            return PdfLoaderStrategy()
        else:
            raise UnsupportedFileError(f"Unsupported file type: {file_extension}")
