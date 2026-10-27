import csv
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


    def split_documents(self, documents: list[Document])->list[Document]:
        """
        Split langchain documents into chunks for better processing.
        """
        return self.text_splitter.split_documents(documents)