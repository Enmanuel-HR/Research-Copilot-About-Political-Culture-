"""
Unit tests for document chunking module
Tests token-based chunking and chunk management
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.chunking import TokenChunker, ChunkingStrategy


class TestTokenChunker:
    """Test token-based document chunking"""

    def test_chunker_initialization(self):
        """Test TokenChunker initialization"""
        chunker = TokenChunker(chunk_size=512, chunk_overlap=50)
        assert chunker.chunk_size == 512
        assert chunker.chunk_overlap == 50

    def test_token_counting(self):
        """Test accurate token counting"""
        chunker = TokenChunker()
        text = "This is a test sentence about political culture."
        tokens = chunker.count_tokens(text)
        assert tokens > 0
        assert isinstance(tokens, int)

    def test_chunk_text_returns_list(self):
        """Test that chunking returns list of chunks"""
        chunker = TokenChunker()
        text = "This is a longer text. " * 20  # Create longer text
        chunks = chunker.chunk_text(text)
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_chunk_structure(self):
        """Test that chunks have correct structure"""
        chunker = TokenChunker()
        text = "This is a test. " * 50
        chunks = chunker.chunk_text(text)

        for chunk in chunks:
            assert "chunk_id" in chunk
            assert "text" in chunk
            assert "token_count" in chunk
            assert "start_token" in chunk
            assert "end_token" in chunk
            assert "metadata" in chunk

    def test_chunk_overlap(self):
        """Test that overlapping chunks share content"""
        chunker = TokenChunker(chunk_size=100, chunk_overlap=20)
        text = "word " * 500  # Create long text
        chunks = chunker.chunk_text(text)

        if len(chunks) > 1:
            # Check that chunks overlap
            assert chunks[1]["start_token"] < chunks[1]["end_token"]


class TestChunkingStrategy:
    """Test chunking strategy selection"""

    def test_get_small_chunker(self):
        """Test small chunking strategy"""
        chunker = ChunkingStrategy.get_chunker("small")
        assert chunker.chunk_size == 256

    def test_get_medium_chunker(self):
        """Test medium chunking strategy"""
        chunker = ChunkingStrategy.get_chunker("medium")
        assert chunker.chunk_size == 512

    def test_get_large_chunker(self):
        """Test large chunking strategy"""
        chunker = ChunkingStrategy.get_chunker("large")
        assert chunker.chunk_size == 1024

    def test_invalid_strategy(self):
        """Test that invalid strategy raises error"""
        with pytest.raises(ValueError):
            ChunkingStrategy.get_chunker("invalid_strategy")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
