from src.services.factories.document_loader_factory import DocumentLoaderFactory
from pathlib import Path
from src.utils.logger import get_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from configs.settings import get_settings
from langchain_core.documents import Document

logger=get_logger(__name__)

class DocumentService:
    """Service for Document Processing"""

    def __init__(self, chunk_size: int | None=None, chunk_overlap: int | None=None):
        settings=get_settings()
        self.chunk_size=chunk_size or settings.chunk_size
        self.chunk_overlap=chunk_overlap or settings.chunk_overlap

        self.text_splitter=RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            length_function=len,
        )


    def load_documents(self, file_path: Path, source_name: str | None=None)->list[Document]:
        document_loader=DocumentLoaderFactory.get_loader(file_path=file_path)
        documents=document_loader.load(file_path=file_path, source_name=source_name)

        logger.info(f"Loaded {len(documents)} documents from {file_path}")
        return documents


    def split_documents(self, documents: list[Document])->list[Document]:
        """
        Split langchain documents into chunks for better processing.
        """
        return self.text_splitter.split_documents(documents)
    

    def process_file(self, file_path: Path, source_name: str | None=None)->list[Document]:
        """
        Process a single file by loading into list of langchain documents and splitting it into chunks.
        """
        documents=self.load_documents(file_path=file_path, source_name=source_name)
        return self.split_documents(documents=documents)


"""
Enhancement using Strategy Design Pattern:

-> Instead of using if-elif chain for different document types in load_documents(), we can use strategy design pattern.

-> We can define a strategy interface "DocumentLoaderStrategy" with a method "load(file_path, source_name)"
and implement it for different document types like "CsvLoaderStrategy", "PdfLoaderStrategy", etc.

-> Instead of using if-elif and creating objects,
We create a Factory class "DocumentLoaderFactory" for document loading that will return the appropriate strategy based on file extension.

-> e.g loader: DocumentLoaderStrategy=DocumentLoaderFactory.get_loader(file_path)
    docs=loader.load(file_path, source_name)

-> Benefits:
    -> Adding new file type support becomes easier. We just need to add new strategy class and update the factory.
"""