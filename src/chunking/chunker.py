"""
Document Chunking Module

Implements multiple chunking strategies for RAG pipeline.
Supports configurable token-based chunking with overlaps.
"""

import tiktoken
from typing import List, Dict, Any, Optional
from loguru import logger


class TokenChunker:
    """
    Token-based document chunker for semantic preservation.

    Uses tiktoken to accurately count tokens based on the model's tokenizer.
    Supports configurable chunk sizes and overlaps.
    """

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        model: str = "gpt-4"
    ):
        """
        Initialize TokenChunker.

        Args:
            chunk_size: Number of tokens per chunk
            chunk_overlap: Number of overlapping tokens between chunks
            model: Model name for tokenizer (gpt-4, gpt-3.5-turbo, etc.)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.model = model
        self.encoder = tiktoken.encoding_for_model(model)

        logger.info(
            f"TokenChunker initialized: size={chunk_size}, "
            f"overlap={chunk_overlap}, model={model}"
        )

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using the model's tokenizer.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        return len(self.encoder.encode(text))

    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks based on token count.

        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
                     (e.g., paper_id, page_number, source)

        Returns:
            List of chunk dictionaries with:
                - chunk_id: Unique chunk identifier
                - text: Chunk text content
                - token_count: Number of tokens in chunk
                - start_token: Starting token position in document
                - end_token: Ending token position in document
                - metadata: Associated metadata
        """
        tokens = self.encoder.encode(text)
        chunks = []

        start = 0
        chunk_id = 0

        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoder.decode(chunk_tokens)

            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata.update({
                "chunk_size_tokens": self.chunk_size,
                "chunk_overlap_tokens": self.chunk_overlap
            })

            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "token_count": len(chunk_tokens),
                "start_token": start,
                "end_token": end,
                "metadata": chunk_metadata
            })

            # Move start position by (chunk_size - overlap)
            start += self.chunk_size - self.chunk_overlap
            chunk_id += 1

            # Stop if we've reached the end
            if end == len(tokens):
                break

        logger.info(
            f"Chunked text into {len(chunks)} chunks "
            f"({len(tokens)} total tokens)"
        )

        return chunks


class ChunkingStrategy:
    """Manages different chunking configurations."""

    # Predefined chunking configurations
    CONFIGS = {
        "small": {
            "chunk_size": 256,
            "chunk_overlap": 25,
            "description": "Small chunks (256 tokens) - Better for precise, factual questions"
        },
        "medium": {
            "chunk_size": 512,
            "chunk_overlap": 50,
            "description": "Medium chunks (512 tokens) - Balanced approach"
        },
        "large": {
            "chunk_size": 1024,
            "chunk_overlap": 100,
            "description": "Large chunks (1024 tokens) - Better for complex, multi-part questions"
        }
    }

    @staticmethod
    def get_chunker(
        strategy: str = "medium",
        model: str = "gpt-4"
    ) -> TokenChunker:
        """
        Get a TokenChunker instance for the specified strategy.

        Args:
            strategy: One of 'small', 'medium', 'large'
            model: Model name for tokenizer

        Returns:
            Configured TokenChunker instance

        Raises:
            ValueError: If strategy is not recognized
        """
        if strategy not in ChunkingStrategy.CONFIGS:
            raise ValueError(
                f"Unknown strategy: {strategy}. "
                f"Available: {list(ChunkingStrategy.CONFIGS.keys())}"
            )

        config = ChunkingStrategy.CONFIGS[strategy]
        logger.info(f"Using {strategy} chunking strategy: {config['description']}")

        return TokenChunker(
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"],
            model=model
        )

    @staticmethod
    def get_all_strategies() -> Dict[str, Dict[str, Any]]:
        """Get all available chunking strategies."""
        return ChunkingStrategy.CONFIGS

    @staticmethod
    def list_strategies() -> None:
        """Print all available strategies."""
        print("\nAvailable Chunking Strategies:")
        print("-" * 60)
        for name, config in ChunkingStrategy.CONFIGS.items():
            print(f"\n{name.upper()}")
            print(f"  Chunk Size: {config['chunk_size']} tokens")
            print(f"  Overlap: {config['chunk_overlap']} tokens")
            print(f"  Description: {config['description']}")
        print("-" * 60)


def chunk_document(
    text: str,
    paper_id: str,
    strategy: str = "medium",
    model: str = "gpt-4"
) -> List[Dict[str, Any]]:
    """
    Convenience function to chunk a document using a strategy.

    Args:
        text: Document text to chunk
        paper_id: Identifier for the source paper
        strategy: Chunking strategy ('small', 'medium', 'large')
        model: Model name for tokenizer

    Returns:
        List of chunks with metadata
    """
    chunker = ChunkingStrategy.get_chunker(strategy, model)
    metadata = {"paper_id": paper_id, "strategy": strategy}
    return chunker.chunk_text(text, metadata)


def chunk_multiple_documents(
    documents: List[Dict[str, str]],
    strategy: str = "medium",
    model: str = "gpt-4"
) -> List[Dict[str, Any]]:
    """
    Chunk multiple documents.

    Args:
        documents: List of dicts with 'text' and 'paper_id' keys
        strategy: Chunking strategy
        model: Model name for tokenizer

    Returns:
        Combined list of all chunks with metadata
    """
    all_chunks = []

    for doc in documents:
        chunks = chunk_document(
            text=doc["text"],
            paper_id=doc["paper_id"],
            strategy=strategy,
            model=model
        )
        all_chunks.extend(chunks)

    logger.info(
        f"Chunked {len(documents)} documents into {len(all_chunks)} chunks"
    )

    return all_chunks
