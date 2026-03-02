"""
RAG Retrieval Module

Handles semantic retrieval of document chunks with metadata enrichment.
Integrates ChromaDB vector search with paper metadata catalog.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger


class RAGRetriever:
    """
    Retrieval module for RAG pipeline.

    Fetches similar chunks from vector database and enriches them with
    metadata from the paper catalog.
    """

    def __init__(
        self,
        vector_store,
        embedder,
        paper_catalog_path: str = "papers/paper_catalog.json"
    ):
        """
        Initialize RAG retriever.

        Args:
            vector_store: ChromaVectorStore instance
            embedder: OpenAIEmbedder instance
            paper_catalog_path: Path to paper metadata catalog
        """
        self.vector_store = vector_store
        self.embedder = embedder

        # Load paper catalog
        self.paper_catalog = self._load_paper_catalog(paper_catalog_path)
        self.paper_map = self._create_paper_map()

        logger.info(f"RAGRetriever initialized with {len(self.paper_catalog)} papers")

    def _load_paper_catalog(self, catalog_path: str) -> List[Dict[str, Any]]:
        """
        Load paper metadata catalog.

        Args:
            catalog_path: Path to paper_catalog.json

        Returns:
            List of paper metadata dictionaries
        """
        try:
            with open(catalog_path, 'r', encoding='utf-8') as f:
                catalog_data = json.load(f)
                return catalog_data.get('papers', [])
        except FileNotFoundError:
            logger.warning(f"Paper catalog not found at {catalog_path}")
            return []

    def _create_paper_map(self) -> Dict[str, Dict[str, Any]]:
        """
        Create mapping from paper_id to paper metadata.

        Returns:
            Dictionary mapping paper_id to paper info
        """
        paper_map = {}
        for paper in self.paper_catalog:
            paper_id = paper.get('id')
            if paper_id:
                paper_map[paper_id] = paper
        return paper_map

    def _enrich_chunk_metadata(
        self,
        chunk_dict: Dict[str, Any],
        similarity_score: float
    ) -> Dict[str, Any]:
        """
        Enrich chunk with paper metadata.

        Args:
            chunk_dict: Chunk from vector store
            similarity_score: Similarity score from search

        Returns:
            Enriched chunk with full metadata
        """
        # Extract paper_id from chunk metadata or ID
        paper_id = chunk_dict.get('metadata', {}).get('paper_id')

        # Get paper info
        paper_info = self.paper_map.get(paper_id, {})

        # Build enriched metadata
        enriched_metadata = {
            "paper_id": paper_id,
            "paper_title": paper_info.get('title', 'Unknown'),
            "authors": self._format_authors(paper_info.get('authors', [])),
            "year": paper_info.get('year', 'Unknown'),
            "page_number": chunk_dict.get('metadata', {}).get('page_number', 'N/A'),
            "section": chunk_dict.get('metadata', {}).get('section', 'N/A'),
            "chunk_size_tokens": chunk_dict.get('metadata', {}).get('chunk_size_tokens', 'N/A'),
            **{k: v for k, v in chunk_dict.get('metadata', {}).items()
               if k not in ['paper_id', 'page_number', 'section', 'chunk_size_tokens']}
        }

        return {
            "chunk_id": chunk_dict.get('chunk_id'),
            "text": chunk_dict.get('text'),
            "metadata": enriched_metadata,
            "similarity_score": similarity_score
        }

    def _format_authors(self, authors: List[str]) -> str:
        """
        Format author list for display.

        Args:
            authors: List of author names

        Returns:
            Formatted author string
        """
        if not authors:
            return "Unknown"
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} and {authors[1]}"
        else:
            return f"{authors[0]} et al."

    def retrieve(
        self,
        query: str,
        k: int = 5,
        similarity_threshold: Optional[float] = None,
        filter_paper_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: Search query text
            k: Number of chunks to retrieve
            similarity_threshold: Minimum similarity score (0-1)
            filter_paper_id: Optional paper ID to filter results

        Returns:
            List of enriched chunks with metadata and scores
        """
        # Generate query embedding
        query_embedding = self.embedder.embed_query(query)

        # Build where clause for filtering
        where = None
        if filter_paper_id:
            where = {"paper_id": filter_paper_id}

        # Query vector store
        results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=k,
            where=where
        )

        # Process and enrich results
        retrieved_chunks = []

        if results and results.get('ids') and len(results['ids']) > 0:
            for i, (chunk_id, text, distance, metadata) in enumerate(zip(
                results['ids'][0],
                results['documents'][0],
                results['distances'][0],
                results['metadatas'][0]
            )):
                # Convert distance to similarity (cosine distance -> similarity)
                similarity_score = 1 - distance

                # Skip if below threshold
                if similarity_threshold and similarity_score < similarity_threshold:
                    continue

                # Create chunk dict for enrichment
                chunk_dict = {
                    'chunk_id': chunk_id,
                    'text': text,
                    'metadata': metadata
                }

                # Enrich with paper metadata
                enriched = self._enrich_chunk_metadata(chunk_dict, similarity_score)
                retrieved_chunks.append(enriched)

        logger.info(
            f"Retrieved {len(retrieved_chunks)} chunks for query: '{query[:50]}...'"
        )

        return retrieved_chunks

    def retrieve_by_paper(
        self,
        paper_id: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all chunks from a specific paper.

        Args:
            paper_id: Paper identifier

        Returns:
            List of all chunks from the paper with metadata
        """
        where = {"paper_id": paper_id}

        results = self.vector_store.collection.get(where=where)

        chunks = []
        if results and results.get('ids'):
            for chunk_id, text, metadata in zip(
                results['ids'],
                results['documents'],
                results['metadatas']
            ):
                chunk_dict = {
                    'chunk_id': chunk_id,
                    'text': text,
                    'metadata': metadata
                }

                # Enrich metadata
                enriched = self._enrich_chunk_metadata(chunk_dict, similarity_score=1.0)
                chunks.append(enriched)

        return chunks

    def get_retrieval_context(
        self,
        chunks: List[Dict[str, Any]],
        include_metadata: bool = True
    ) -> str:
        """
        Format retrieved chunks for LLM context.

        Args:
            chunks: List of retrieved chunks
            include_metadata: Whether to include metadata

        Returns:
            Formatted context string for LLM
        """
        context_parts = []

        for i, chunk in enumerate(chunks, 1):
            if include_metadata:
                header = (
                    f"[Source {i}] {chunk['metadata'].get('paper_title', 'Unknown')} "
                    f"({chunk['metadata'].get('year', 'N/A')}) - "
                    f"{chunk['metadata'].get('authors', 'Unknown')} "
                    f"(Relevance: {chunk['similarity_score']:.2%})"
                )
                context_parts.append(header)

            context_parts.append(chunk['text'])
            context_parts.append("")  # Blank line

        return "\n".join(context_parts)

    def print_retrieval_results(
        self,
        chunks: List[Dict[str, Any]],
        query: str
    ) -> None:
        """
        Print formatted retrieval results.

        Args:
            chunks: Retrieved chunks
            query: Original query
        """
        print("\n" + "=" * 80)
        print("RETRIEVAL RESULTS")
        print("=" * 80)
        print(f"Query: {query}")
        print(f"Retrieved: {len(chunks)} chunks\n")

        for i, chunk in enumerate(chunks, 1):
            print(f"Result {i}:")
            print(f"  Paper: {chunk['metadata'].get('paper_title', 'Unknown')}")
            print(f"  Authors: {chunk['metadata'].get('authors', 'Unknown')}")
            print(f"  Year: {chunk['metadata'].get('year', 'N/A')}")
            print(f"  Relevance: {chunk['similarity_score']:.2%}")
            print(f"  Text: {chunk['text'][:150]}...")
            print()

        print("=" * 80 + "\n")


def create_retriever(
    vector_store,
    embedder,
    paper_catalog_path: str = "papers/paper_catalog.json"
) -> RAGRetriever:
    """
    Factory function to create a RAG retriever.

    Args:
        vector_store: ChromaVectorStore instance
        embedder: OpenAIEmbedder instance
        paper_catalog_path: Path to paper catalog

    Returns:
        Configured RAGRetriever instance
    """
    return RAGRetriever(vector_store, embedder, paper_catalog_path)
