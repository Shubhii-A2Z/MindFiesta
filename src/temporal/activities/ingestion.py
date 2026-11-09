from src.utils.document_chunk_writing import read_documents_from_jsonl_batch
import json
from src.utils.document_chunk_writing import count_jsonl_lines
from src.utils.document_chunk_writing import write_documents_to_jsonl
from src.utils.document_chunk_writing import spill_path_for_upload
from src.services.ingestion_service import IngestionService
from src.configs.settings import get_settings
from src.repositories.vector_store_repository import VectorStoreRepository
from pathlib import Path
from src.services.document_service import DocumentService
from temporalio import activity
from src.utils.logger import get_logger
from langchain_core.documents import Document

logger=get_logger(__name__)

def _to_dict(documents: list[Document])->list[dict]:
    return [
        {
            "page_content": doc.page_content,
            "metadata": doc.metadata
        }
        for doc in documents
    ]


def _from_dict(documents: list[dict])->list[Document]:
    """Convert list of dicts to list of langchain Documents for temporal"""

    return [
        Document(page_content=doc["page_content"], metadata=doc["metadata"])
        for doc in documents
    ]

@activity.defn(name="ingest_file_activity")
async def ingest_file_activity(
    local_path: str,
    filename: str,
    batch_size: int | None=None
)->int:
    """Temporal activity to ingest a file"""

    settings=get_settings()
    batch_size=batch_size or settings.index_batch_size

    activity.logger.info(f"Ingesting file {filename} from {local_path} with batch_size {batch_size}")

    def _heartbeat(indexed: int, total: int)->None:
        activity.heartbeat(f"Indexed {indexed} of {total} chunks")

    service=IngestionService()
    result=service.ingest_file_at_path(
        file_path=Path(local_path),
        source_name=filename,
        index_batch_size=batch_size,
        on_index_callable=_heartbeat
    )

    return result["chunks_created"]


@activity.defn(name="parse_document_activity")
async def parse_document_activity(local_path: str, filename: str)->list[dict]:
    """Temporal activity to parse a document"""

    activity.logger.info(f"Parsing documents from {local_path} with filename {filename}")
    service=DocumentService()
    documents=service.load_documents(Path(local_path), source_name=filename)
    return _to_dict(documents)


@activity.defn(name="chunk_document_activity")
async def chunk_document_activity(documents: list[dict])->list[dict]:
    """Temporal activity to chunk documents"""
    
    activity.logger.info(f"Chunking {len(documents)} documents")
    service=DocumentService()
    documents=service.split_documents(_from_dict(documents))
    return _to_dict(documents)


@activity.defn(name="index_document_activity")
async def index_document_activity(chunks: list[dict])->int:
    """Temporal activity to index chunks in Vector DB"""

    if not chunks:
        return 0

    repository=VectorStoreRepository()

    # converting dict to list langchain Documents
    chunks=_from_dict(chunks)

    # adding chunks to vector store
    ids=repository.add_documents(documents=chunks)

    # Logging the number of chunks indexed
    activity.logger.info(f"Indexed {len(chunks)} documents")
    
    return len(chunks)


@activity.defn(name="parse_documents_to_jsonl_activity")
async def parse_documents_to_jsonl_activity(local_path: Path, filename: str)->dict:
    """Activity to parse documents from local path and write them to a jsonl file at the disk/write path"""

    upload_path=Path(local_path)
    write_path=spill_path_for_upload(upload_path=upload_path, filename=filename, stage="parsed")

    activity.logger.info(f"Parsing documents from {local_path} with filename {filename} to {write_path}")
    service=DocumentService()
    docs=service.load_documents(upload_path, filename)

    count=write_documents_to_jsonl(path=write_path, documents=docs)
    line_count=count_jsonl_lines(path=write_path)

    return {
        "write_path": write_path,
        "line_count": line_count,
        "staged": "parsed"
    }


@activity.defn(name="chunk_documents_to_jsonl_activity")
async def chunk_documents_to_jsonl_activity(parse_path: Path, filename: str)->dict:
    """Activity to chunk documents from a parsed jsonl file and write them to a chunks jsonl file at the disk/write path"""

    parse_path=Path(parse_path)

    # Parent directory
    upload_path=parse_path.parent.parent / Path(filename).name

    # construct chunks_path for writing chunk to disk
    chunks_path=spill_path_for_upload(upload_path=upload_path, filename=filename, stage="chunks")

    service=DocumentService()
    documents=[]

    # opening the parsed jsonl file and loading the documents from the disk for chunking
    with parse_path.open("r", encoding="utf-8") as f:
        for line in f:
            text=line.strip()
            if not text:
                continue
            payload=json.loads(text)
            documents.append(Document(page_content=payload["page_content"], metadata=payload["metadata"]))
    
    # Chunking the documents
    chunks=service.split_documents(documents=documents)

    # Writing the chunks to the disk or chunks_path
    count=write_documents_to_jsonl(path=chunks_path, documents=chunks)

    line_count=count_jsonl_lines(path=chunks_path)
    activity.logger.info(f"Chunked {count} documents loaded from {parse_path} with filename {filename} and written to {chunks_path}")

    return {
        "chunks_count": count,
        "line_count": line_count,
        "chunks_path": chunks_path,
        "stage": "chunks"
    }


@activity.defn(name="index_document_from_jsonl_activity")
async def index_document_from_jsonl_activity(chunks_path: Path, offset: int, batch_size: int)->dict:
    """Activity to index documents from a chunks jsonl file and add them to the vector store"""

    chunks_path=Path(chunks_path)
    
    # Reading the chunks from disk in a paginated format
    batch=read_documents_from_jsonl_batch(path=chunks_path, offset=offset, limit=batch_size)

    if not batch:
        return 0
    
    repository=VectorStoreRepository()
    ids=repository.add_documents(documents=batch)
    activity.heartbeat(f"Indexed {len(ids)} chunks from {chunks_path} with offset {offset} and batch_size {batch_size}")

    return len(ids)