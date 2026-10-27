import uuid
from langchain_core.documents import Document
from qdrant_client.conversions.common_types import Distance
from qdrant_client.conversions.common_types import VectorParams
from src.services.embedding_service import get_embeddings
from src.configs.qdrant_config import get_qdrant_client
from configs.settings import get_settings
from langchain_qdrant import QdrantVectorStore
from doctest import UnexpectedException

EMBEDDING_DIMENSIONS=1536

class VectorStoreRepository:

    def __init__(self, collection_name: str | None=None):
        settings=get_settings()

        # Creating collection, similar to tables
        self.collection_name=collection_name or settings.collection_name

        # Qdrant client to interact with Qdrant instance
        self.client=get_qdrant_client()

        # Vector store for the application
        self._vector_store: QdrantVectorStore | None=None

    # Property decorator used so that we can use it like "self.vector_store" without parentheses
    @property
    def vector_store(self)->QdrantVectorStore:
        if self._vector_store is None:
            self._vector_store=QdrantVectorStore(
                client=self.client,
                collection_name=self.collection_name,
                embedding=get_embeddings(),
            )
        return self._vector_store


    def _ensure_collection_exists(self)->None:
        """
        Check if the collection exists, if not create it
        """
        try:
            _info=self.client.get_collection(collection_name=self.collection_name)
        except UnexpectedException:
            print(f"Collection {self.collection_name} not found. Creating ...")

            self.client.create_collection(
                collection_name=self.collection_name,
                # Inside db how vectors should be configured
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSIONS, # Vector dimensions which should match the embedding model
                    distance=Distance.COSINE, # Cosine similarity
                )
            )
    

    def add_documents(self, documents: list[Document])->list[str]:
        if documents is None:
            return []
        
        # Create unique ids for each document
        ids=[str(uuid.uuid4()) for _ in documents]

        # Adding documents to vector store db
        self.vector_store.add_documents(documents=documents, ids=ids)

        return ids
    

    def delete_collection(self)->None:
        self.client.delete_collection(collection_name=self.collection_name)