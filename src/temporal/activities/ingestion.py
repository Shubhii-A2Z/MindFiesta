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