from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from src.configs.settings import get_settings
from src.repositories.vector_store_repository import VectorStoreRepository
from src.utils.logger import get_logger

logger=get_logger(__name__)


RAG_PROMPT="""
You are an helpful assistant. Answer the question based on the provided context.

If you cannot answer from the context, say "I don't have enough information to answer that question".
Do not make up information.

Context:
{context}

Question: {question}

Answer:
"""


class RAGQueryService:

    def __init__(self, vector_store: VectorStoreRepository | None=None):
        self.settings=get_settings()
        self.vector_store=vector_store or VectorStoreRepository()
        self.retriever=self.vector_store.get_retriever()
        self.llm=ChatGoogleGenerativeAI(
            model=self.settings.llm_model,
            temperature=self.settings.llm_temperature,
            google_api_key=self.settings.google_api_key
        )

        prompt=ChatPromptTemplate(RAG_PROMPT)

        self.chain=(
            {
                "context": self.retriever,
                "question": RunnablePassthrough()
            }
        ) | prompt | self.llm | StrOutputParser()


    async def aquery(self, question: str)->dict:
        """Query the RAG system with question"""

        answer=await self.chain.ainvoke({"question": question})
        return {
            "answer": answer
        }


    async def aquery_with_source(self, question: str)->dict:
        """Query the RAG system with question and return the answer and source"""

        answer=await self.chain.ainvoke({"question": question})

        # Retrieve the list of LangChain Document objects containing the matching content and metadata.
        source=self.retriever.invoke(question)

        return {
            "answer": answer,
            "source": source
        }


    def stream(self, question: str):
        """Stream the response from the RAG system with question"""

        yield from self.chain.stream({"question": question})
    

    def _format_source(self, docs: list[Document])->dict:
        """Format the source documents"""

        sources=[]

        for doc in docs:
            content=doc.page_content
            if len(content)>500:
                content=content[:500]+"..."
            sources.append({
                "content": content,
                "metadata": doc.metadata
            })

        return sources

