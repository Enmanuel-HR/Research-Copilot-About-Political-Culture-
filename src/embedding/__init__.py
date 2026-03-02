"""
Embedding module for vector generation and embeddings management.

Uses OpenAI's embedding models to convert text into vector representations.
"""

from .embedder import OpenAIEmbedder, create_embedder

__all__ = ["OpenAIEmbedder", "create_embedder"]
