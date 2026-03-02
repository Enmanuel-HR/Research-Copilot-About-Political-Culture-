"""
Retrieval module for RAG similarity search and chunk retrieval.

Implements semantic search with metadata enrichment and filtering.
"""

from .retriever import RAGRetriever, create_retriever

__all__ = ["RAGRetriever", "create_retriever"]
