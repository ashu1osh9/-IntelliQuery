"""
Retriever setup and vector store configuration.

Uses Qdrant (cloud-hosted, persistent) as the vector store instead of the
previous in-memory FAISS setup, so uploaded documents survive backend
restarts.
"""

import os

from langchain_core.tools import create_retriever_tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from src.core.config import settings

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

qdrant_client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)


def _ensure_collection() -> None:
    """Create the Qdrant collection if it doesn't already exist."""
    existing = [c.name for c in qdrant_client.get_collections().collections]
    if settings.DOCS_COLLECTION not in existing:
        # Probe the embedding model's actual output size rather than
        # hardcoding it, so this keeps working if the model changes.
        dim = len(embeddings.embed_query("dimension probe"))
        qdrant_client.create_collection(
            collection_name=settings.DOCS_COLLECTION,
            vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
        )
        print(f"Created Qdrant collection '{settings.DOCS_COLLECTION}' (dim={dim})")


def _get_vectorstore() -> QdrantVectorStore:
    _ensure_collection()
    return QdrantVectorStore(
        client=qdrant_client,
        collection_name=settings.DOCS_COLLECTION,
        embedding=embeddings,
    )


def retriever_chain(chunks: list) -> bool:
    """
    Add document chunks to the Qdrant collection.

    Args:
        chunks: List of document chunks to store.

    Returns:
        Boolean indicating success of the operation.
    """
    try:
        vectorstore = _get_vectorstore()
        vectorstore.add_documents(chunks)
        print(f"Added {len(chunks)} chunks to Qdrant collection '{settings.DOCS_COLLECTION}'")
        return True
    except Exception as e:
        print(f"Error storing documents in Qdrant: {e}")
        return False


def get_retriever():
    """
    Get a retriever tool connected to the Qdrant vector store.

    Always queries the live Qdrant collection, so it reflects whatever was
    most recently uploaded (including from a previous run, since Qdrant
    persists data).

    Returns:
        A LangChain retriever tool configured for the vector store.

    Raises:
        Exception: If vector store initialization fails.
    """
    try:
        vectorstore = _get_vectorstore()
        retriever = vectorstore.as_retriever()

        if os.path.exists("description.txt"):
            with open("description.txt", "r", encoding="utf-8") as f:
                description = f.read()
        else:
            description = None

        retriever_tool = create_retriever_tool(
            retriever,
            "retriever_customer_uploaded_documents",
            f"Use this tool **only** to answer questions about: {description}\n"
            "Don't use this tool to answer anything else."
        )

        return retriever_tool

    except Exception as e:
        print(f"Error initializing retriever: {e}")
        raise Exception(e)