"""
Embedding Generation Module

Handles generation of vector embeddings using OpenAI's API.
Supports batch processing and cost tracking.
"""

from openai import OpenAI
from typing import List, Dict, Any, Optional
import math
from loguru import logger


class OpenAIEmbedder:
    """
    Generates embeddings using OpenAI's embedding models.

    Uses text-embedding-3-small by default (most cost-effective).
    Supports batch processing and includes cost tracking.
    """

    # Model pricing (per 1M tokens) - as of Feb 2026
    PRICING = {
        "text-embedding-3-small": 0.02,  # $0.02 per 1M tokens
        "text-embedding-3-large": 0.13,  # $0.13 per 1M tokens
    }

    def __init__(self, model: str = "text-embedding-3-small"):
        """
        Initialize OpenAI embedder.

        Args:
            model: Model name (text-embedding-3-small or text-embedding-3-large)

        Raises:
            ValueError: If model is not supported
        """
        if model not in self.PRICING:
            raise ValueError(f"Unsupported model: {model}. Available: {list(self.PRICING.keys())}")

        self.client = OpenAI()
        self.model = model
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.embedding_calls = 0

        logger.info(f"OpenAIEmbedder initialized with model: {model}")

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embeddings (each embedding is a list of floats)

        Raises:
            ValueError: If texts list is empty
            Exception: If API call fails
        """
        if not texts:
            raise ValueError("Cannot embed empty text list")

        if len(texts) > 100:
            logger.warning(f"Large batch of {len(texts)} texts. Consider processing in smaller batches.")

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )

            # Track usage
            self.total_tokens_used += response.usage.prompt_tokens
            self.embedding_calls += 1

            # Calculate cost
            cost = (response.usage.prompt_tokens / 1_000_000) * self.PRICING[self.model]
            self.total_cost += cost

            logger.info(
                f"Generated {len(response.data)} embeddings using {response.usage.prompt_tokens} tokens. "
                f"Cost: ${cost:.6f} | Total cost: ${self.total_cost:.6f}"
            )

            return [item.embedding for item in response.data]

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.

        Args:
            query: Query text to embed

        Returns:
            Embedding vector (list of floats)
        """
        return self.embed_texts([query])[0]

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for many texts in batches.

        Useful for large document collections to avoid API limits.

        Args:
            texts: List of all texts to embed
            batch_size: Number of texts per API call (max 100)

        Returns:
            List of all embeddings in same order as input texts
        """
        if batch_size > 100:
            batch_size = 100
            logger.warning("Batch size limited to 100 (API maximum)")

        all_embeddings = []
        num_batches = math.ceil(len(texts) / batch_size)

        logger.info(f"Processing {len(texts)} texts in {num_batches} batches of {batch_size}")

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1

            embeddings = self.embed_texts(batch)
            all_embeddings.extend(embeddings)

            logger.info(f"Batch {batch_num}/{num_batches} completed")

        return all_embeddings

    def embed_chunks(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Generate embeddings for document chunks and add to metadata.

        Args:
            chunks: List of chunk dicts with 'text' key
            batch_size: Number of chunks per API call

        Returns:
            List of chunks with 'embedding' key added
        """
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embed_batch(texts, batch_size)

        # Add embeddings to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding

        logger.info(f"Generated embeddings for {len(chunks)} chunks")

        return chunks

    def get_cost_report(self) -> Dict[str, Any]:
        """
        Get a report of embedding generation costs.

        Returns:
            Dictionary with cost information
        """
        return {
            "model": self.model,
            "total_calls": self.embedding_calls,
            "total_tokens": self.total_tokens_used,
            "total_cost": self.total_cost,
            "cost_per_call": self.total_cost / self.embedding_calls if self.embedding_calls > 0 else 0,
            "tokens_per_call": self.total_tokens_used / self.embedding_calls if self.embedding_calls > 0 else 0,
        }

    def print_cost_report(self) -> None:
        """Print formatted cost report."""
        report = self.get_cost_report()
        print("\n" + "=" * 60)
        print("EMBEDDING COST REPORT")
        print("=" * 60)
        print(f"Model: {report['model']}")
        print(f"Total API Calls: {report['total_calls']}")
        print(f"Total Tokens Used: {report['total_tokens']:,}")
        print(f"Avg Tokens per Call: {report['tokens_per_call']:.1f}")
        print(f"Total Cost: ${report['total_cost']:.6f}")
        print(f"Avg Cost per Call: ${report['cost_per_call']:.6f}")
        print("=" * 60 + "\n")


def create_embedder(model: str = "text-embedding-3-small") -> OpenAIEmbedder:
    """
    Factory function to create an OpenAI embedder.

    Args:
        model: Model name

    Returns:
        Configured OpenAIEmbedder instance
    """
    return OpenAIEmbedder(model)
