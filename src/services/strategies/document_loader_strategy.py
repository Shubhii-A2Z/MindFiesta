from pathlib import Path
from abc import ABC, abstractmethod
from langchain_core.documents import Document

class DocumentLoaderStrategy(ABC):

    @abstractmethod
    def load(self, file_path: Path, source_name: str | None=None)->list[Document]:
        pass