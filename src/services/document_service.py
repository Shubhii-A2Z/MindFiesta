from src.exceptions.unsupported_file_error import UnsupportedFileError
import csv
from pathlib import Path
from src.utils.logger import get_logger
from langchain_text_splitters import RecursiveCharacterTextSplitter
from configs.settings import get_settings
from langchain_core.documents import Document

logger=get_logger(__name__)

class DocumentService:
    """Service for Document Processing"""

    SUPPORTED_FILE_EXTENSIONS={".csv"}

    TRANSCRIPT_CSV_FIELDNAMES={
        "id",
        "start",
        "end",
        "text",
        "url",
        "channel_id",
        "title",
        "published",
    }
    

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


    def _is_transcript_csv(self, file_path: Path)->bool:
        """Check if the file is valid transcript csv"""
        with file_path.open(newline="", encoding="utf-8") as file:
            reader=csv.DictReader(file)

            if not reader.fieldnames:
                return False
            
            fields=set[str](reader.fieldnames)
            return self.TRANSCRIPT_CSV_FIELDNAMES.issubset(fields)


    def load_transcript_csv(self, file_path: Path, source_name: str)->list[Document]:
        """Load a transcript csv file into list of Documents. Every row will be a document in vector db"""

        documents: list[Document]=[]

        with file_path.open("r", encoding="utf-8") as file:
            # Reading CSV as key-value pairs, one row as one dictionary
            # e.g. [{'text': 'Hello', 'start': '0', 'end': '1'}, {'text': 'World', 'start': '1', 'end': '2'}]
            reader=csv.DictReader(file)

            # going to every row/dictionary
            for row in reader:
                text=row.get("text").strip()

                if not text:
                    continue

                metadata={
                    "source": source_name,
                    "id": row.get("id"),
                    "start": row.get("start"),
                    "end": row.get("end"),
                    "url": row.get("url"),
                    "channel_id": row.get("channel_id"),
                    "title": row.get("title"),
                    "published": row.get("published"),
                }

                # Creating Document object for this row
                documents.append(Document(page_content=text, metadata=metadata))
        
        logger.info(f"Extracted and loaded {len(documents)} documents from {file_path}")
        return documents
    

    def load_documents(self, file_path: Path, source_name: str | None=None)->list[Document]:
        file_path=Path(file_path)
        source=source_name or file_path.name

        # Getting the document extension type (.csv, .txt, .pdf, etc)
        file_extension=file_path.suffix.lower()

        if file_extension not in self.SUPPORTED_FILE_EXTENSIONS:
            raise UnsupportedFileError(f"Unsupported file type: {file_extension}")

        if file_extension==".csv":
            if self._is_transcript_csv(file_path):
                docs=self.load_transcript_csv(file_path=file_path, source_name=source)
            else:
                raise ValueError(f"Unsupported CSV file: {file_path}")
        
        return docs


    def split_documents(self, documents: list[Document])->list[Document]:
        """
        Split langchain documents into chunks for better processing.
        """
        return self.text_splitter.split_documents(documents)
    

    def process_file(self, file_path: Path, source_name: str | None=None)->list[Document]:
        """
        Process a single file by loading and splitting it into chunks.
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