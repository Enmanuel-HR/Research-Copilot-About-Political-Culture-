"""
ChromaDB Vector Store Module

Handles storage and retrieval of document embeddings using ChromaDB.
Supports semantic similarity search and metadata filtering.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger


class ChromaVectorStore:
    """
    Vector database wrapper for ChromaDB.

    Manages storage of document embeddings and provides semantic search capabilities.
    Uses persistent storage for durability.
    """

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB persistent client.

        Args:
            persist_directory: Path to store ChromaDB data
        """
        # Create directory if it doesn't exist
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = None
        self.persist_directory = persist_directory

        logger.info(f"ChromaDB initialized with persistent storage at {persist_directory}")

    def create_collection(self, name: str) -> None:
        """
        Create or get a collection.

        Args:
            name: Name of the collection
        """
        self.collection = self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )

        logger.info(f"Collection '{name}' created or retrieved")

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]]
    ) -> None:
        """
        Add documents with embeddings and metadata to the collection.

        Args:
            ids: List of unique document IDs
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries

        Raises:
            ValueError: If collection is not created
            ValueError: If lists have mismatched lengths
        """
        if self.collection is None:
            raise ValueError("Collection not created. Call create_collection() first.")

        if not (len(ids) == len(documents) == len(embeddings) == len(metadatas)):
            raise ValueError("All input lists must have the same length")

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        logger.info(f"Added {len(ids)} documents to collection '{self.collection.name}'")

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query similar documents using embedding similarity.

        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Optional metadata filter (ChromaDB where clause)

        Returns:
            Dictionary with query results:
                - ids: Document IDs
                - documents: Document texts
                - metadatas: Metadata dictionaries
                - distances: Cosine distances (0-2, lower is more similar)

        Raises:
            ValueError: If collection is not created
        """
        if self.collection is None:
            raise ValueError("Collection not created. Call create_collection() first.")

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )

        logger.info(f"Retrieved {len(results['ids'][0])} similar documents")

        return results

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection.

        Returns:
            Dictionary with collection statistics
        """
        if self.collection is None:
            return {"status": "No collection created"}

        count = self.collection.count()

        return {
            "collection_name": self.collection.name,
            "document_count": count,
            "embedding_dimension": 1536,  # text-embedding-3-small standard
            "persist_directory": self.persist_directory
        }

    def print_stats(self) -> None:
        """Print formatted collection statistics."""
        stats = self.get_collection_stats()

        print("\n" + "=" * 70)
        print("VECTOR STORE STATISTICS")
        print("=" * 70)

        if "status" in stats:
            print(f"Status: {stats['status']}")
        else:
            print(f"Collection: {stats['collection_name']}")
            print(f"Total Documents: {stats['document_count']}")
            print(f"Embedding Dimension: {stats['embedding_dimension']}")
            print(f"Storage: {stats['persist_directory']}")

        print("=" * 70 + "\n")

    def delete_collection(self) -> None:
        """
        Delete the entire collection (irreversible operation!).

        Use with caution.
        """
        if self.collection is None:
            logger.warning("No collection to delete")
            return

        collection_name = self.collection.name
        self.client.delete_collection(name=collection_name)
        self.collection = None

        logger.warning(f"Deleted collection: {collection_name}")

    def persist(self) -> None:
        """Persist data to disk."""
        self.client.persist()
        logger.info("Vector store persisted to disk")


def create_vector_store(
    persist_directory: str = "./chroma_db"
) -> ChromaVectorStore:
    """
    Factory function to create a ChromaDB vector store.

    Args:
        persist_directory: Directory for persistent storage

    Returns:
        Configured ChromaVectorStore instance
    """
    return ChromaVectorStore(persist_directory)
