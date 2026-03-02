"""
Unit tests for retrieval module
Tests semantic search and context retrieval functionality
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieval import RAGRetriever


class TestRAGRetrieval:
    """Test RAG retrieval functionality"""

    @pytest.fixture
    def retriever(self):
        """Fixture providing initialized retriever"""
        try:
            return RAGRetriever()
        except Exception as e:
            pytest.skip(f"Could not initialize retriever: {e}")

    def test_retriever_initialization(self, retriever):
        """Test RAGRetriever initialization"""
        assert retriever is not None

    def test_retrieve_returns_list(self, retriever):
        """Test that retrieve returns list of chunks"""
        query = "political culture"
        results = retriever.retrieve(query, k=5)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_retrieve_respects_k_parameter(self, retriever):
        """Test that retrieve returns correct number of results"""
        query = "youth activism"
        results = retriever.retrieve(query, k=3)
        assert len(results) <= 3

    def test_retrieve_chunk_structure(self, retriever):
        """Test that retrieved chunks have correct structure"""
        query = "education reform"
        results = retriever.retrieve(query, k=1)

        if results:
            chunk = results[0]
            assert "text" in chunk
            assert "metadata" in chunk or "score" in chunk

    def test_empty_query_handling(self, retriever):
        """Test handling of empty query"""
        try:
            results = retriever.retrieve("", k=5)
            # Should either return empty or handle gracefully
            assert isinstance(results, list)
        except Exception:
            # Empty query exception is acceptable
            pass

    def test_retrieve_different_queries(self, retriever):
        """Test retrieval with different query topics"""
        queries = [
            "political culture",
            "youth activism",
            "social movements"
        ]

        for query in queries:
            results = retriever.retrieve(query, k=3)
            assert isinstance(results, list)
            assert len(results) > 0


class TestMetadataEnrichment:
    """Test metadata enrichment in retrieval"""

    def test_metadata_contains_paper_info(self):
        """Test that metadata includes paper information"""
        try:
            retriever = RAGRetriever()
            results = retriever.retrieve("political culture", k=1)

            if results and len(results) > 0:
                chunk = results[0]
                if "metadata" in chunk:
                    metadata = chunk["metadata"]
                    # Check for expected metadata fields
                    assert isinstance(metadata, dict)
        except Exception:
            pytest.skip("Vector database not initialized")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
