"""
Vector store module for ChromaDB operations.

Handles persistent storage and retrieval of document embeddings.
"""

from .chroma_store import ChromaVectorStore, create_vector_store

__all__ = ["ChromaVectorStore", "create_vector_store"]
