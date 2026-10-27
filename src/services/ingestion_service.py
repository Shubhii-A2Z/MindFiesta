from datasets.utils.logging import get_logger
import uuid
from pathlib import Path
from src.repositories.vector_store_repository import VectorStoreRepository
from src.services.document_service import DocumentService
from configs.settings import get_settings

logger=get_logger(__name__)

class IngestionService:

    def __init__(self):
        self.settings=get_settings()
        self.document_service=DocumentService()
        self.vector_store_repository=VectorStoreRepository()


    def save_upload_batch(self, file_pairs: list[tuple[str, bytes]])->tuple[str, list[Path]]:
        """Save batch of files to the upload directory on local machine"""

        batch_id=str(uuid.uuid4())
        batch_directory=Path(self.settings.upload_dir) / batch_id
        batch_directory.mkdir(parents=True, exist_ok=True)

        paths: list[Path]=[]

        for file_name, content in file_pairs:
            safename=Path(file_name).name
            destination=batch_directory / safename
            destination.write_bytes(content)
            paths.append(destination)
            logger.info(f"Saved {file_name} to {destination}")

        return batch_id, paths


    def ingest_file_at_path(self, file_path: Path, source_name: str | None=None)->dict:
        """Ingest a single file located at file_path into vector store."""

        name=source_name or file_path.name

        # processing and splitting into chunks
        chunks=self.document_service.process_file(file_path=file_path, source_name=name)
        if not chunks:
            return {"filename": name, "chunks_created": 0, "document_ids": []}
        
        # adding the chunks to the vector store
        ids=self.vector_store_repository.add_documents(documents=chunks)
        return {"filename": name, "chunks_created": len(chunks), "document_ids": ids}


    def ingest_file_sync(self, file_pairs: list[tuple[str, bytes]])->dict:
        """Storing the file in local machine and ingesting them in vector stor in sync manner"""

        # saving the files in local machine
        _, paths=self.save_upload_batch(file_pairs=file_pairs)
        results=[]

        # Ingesting every file in sync manner
        for path in paths:
            results.append(self.ingest_file_at_path(file_path=path))
        total_chunks=sum(result["chunks_created"] for result in results)

        return {
            "chunks_created": total_chunks,
            "files": results,
            "total_files": len(results),
            "message": "Document uploaded and indexed successfully"
        }