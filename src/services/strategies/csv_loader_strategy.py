from src.utils.logger import get_logger
from pathlib import Path
from src.services.strategies.document_loader_strategy import DocumentLoaderStrategy
from langchain_core.documents import Document
import csv

logger=get_logger(__name__)

class CsvLoaderStrategy(DocumentLoaderStrategy):

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

    def load(self, file_path: Path, source_name: str | None=None)->list[Document]:
        """Load a transcript csv file into list of Documents. Every row will be a document in vector db"""

        file_path=Path(file_path)

        # Checking if the file is a valid transcript csv
        if not self._is_transcript_csv(file_path):
            raise ValueError(f"Unsupported CSV file: {file_path}")

        documents: list[Document]=[]

        with file_path.open("r", encoding="utf-8") as file:
            # Reading CSV as key-value pairs, one row as one dictionary
            # e.g. [{'text': 'Hello', 'start': '0', 'end': '1'}, {'text': 'World', 'start': '1', 'end': '2'}]
            reader=csv.DictReader(file)

            # going to every row/dictionary
            for row in reader:
                text=row.get("text", "").strip()

                if not text:
                    continue

                metadata={
                    "source": source_name,
                    "id": row.get("id", ""),
                    "start": row.get("start", ""),
                    "end": row.get("end", ""),
                    "url": row.get("url", ""),
                    "channel_id": row.get("channel_id", ""),
                    "title": row.get("title", ""),
                    "published": row.get("published", ""),
                }

                # Creating Document object for this row
                documents.append(Document(page_content=text, metadata=metadata))
        
        logger.info(f"Extracted and loaded {len(documents)} documents from {file_path}")
        return documents
    

    def _is_transcript_csv(self, file_path: Path)->bool:
        """Check if the file is valid transcript csv"""
        with file_path.open(newline="", encoding="utf-8") as file:
            reader=csv.DictReader(file)

            if not reader.fieldnames:
                return False
            
            fields=set[str](reader.fieldnames)
            return self.TRANSCRIPT_CSV_FIELDNAMES.issubset(fields)
