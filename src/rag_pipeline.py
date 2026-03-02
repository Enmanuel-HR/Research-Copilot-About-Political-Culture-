"""
RAG Pipeline Orchestration
Main module that coordinates the complete RAG workflow
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import sys
from loguru import logger

# Import all RAG components
from src.ingestion import extract_text_from_pdf
from src.chunking import TokenChunker
from src.embedding import OpenAIEmbedder
from src.vectorstore import ChromaVectorStore
from src.retrieval import RAGRetriever
from src.generation import RAGGenerator
import config


class RAGPipeline:
    """
    Complete Retrieval-Augmented Generation Pipeline

    Coordinates document processing, embedding, storage, retrieval, and generation
    """

    def __init__(self, strategy: str = "v1"):
        """
        Initialize RAG Pipeline

        Args:
            strategy: Prompt strategy (v1, v2, v3, v4)
        """
        self.strategy = strategy
        self.retriever = None
        self.generator = None

        logger.info(f"Initializing RAG Pipeline with strategy: {strategy}")
        self._initialize_components()

    def _initialize_components(self):
        """Initialize all RAG components"""
        try:
            self.retriever = RAGRetriever()
            self.generator = RAGGenerator(strategy=self.strategy)
            logger.info("RAG Pipeline components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG components: {e}")
            raise

    def ingest_documents(self, pdf_directory: str) -> int:
        """
        Ingest all PDF documents from a directory

        Args:
            pdf_directory: Path to directory containing PDFs

        Returns:
            Number of documents successfully processed
        """
        logger.info(f"Starting document ingestion from: {pdf_directory}")

        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            logger.error(f"Directory not found: {pdf_directory}")
            return 0

        pdf_files = list(pdf_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")

        processed = 0
        for pdf_path in pdf_files:
            try:
                result = extract_text_from_pdf(str(pdf_path))
                if result and result.get("text"):
                    processed += 1
                    logger.info(f"Processed: {pdf_path.name}")
            except Exception as e:
                logger.warning(f"Failed to process {pdf_path.name}: {e}")

        logger.info(f"Document ingestion complete: {processed}/{len(pdf_files)}")
        return processed

    def query(self, question: str, k: int = 5) -> Dict[str, Any]:
        """
        Execute a complete RAG query

        Args:
            question: User's question
            k: Number of chunks to retrieve

        Returns:
            Dictionary with answer and metadata
        """
        logger.info(f"Processing query: {question[:100]}...")

        try:
            # Step 1: Retrieve relevant chunks
            retrieved = self.retriever.retrieve(question, k=k)
            logger.info(f"Retrieved {len(retrieved)} relevant chunks")

            # Step 2: Generate answer
            answer = self.generator.generate(question, retrieved)
            logger.info("Answer generated successfully")

            # Compile result
            result = {
                "question": question,
                "answer": answer,
                "retrieved_chunks": len(retrieved),
                "strategy": self.strategy,
                "status": "success"
            }

            return result

        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                "question": question,
                "error": str(e),
                "status": "error"
            }

    def change_strategy(self, new_strategy: str):
        """
        Change the prompt generation strategy

        Args:
            new_strategy: New strategy to use (v1, v2, v3, v4)
        """
        self.strategy = new_strategy
        self.generator = RAGGenerator(strategy=new_strategy)
        logger.info(f"Strategy changed to: {new_strategy}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get pipeline statistics

        Returns:
            Dictionary with pipeline metrics
        """
        return {
            "strategy": self.strategy,
            "embedding_calls": self.retriever.embedding_calls if hasattr(self.retriever, 'embedding_calls') else 0,
            "generation_calls": self.generator.generation_calls if hasattr(self.generator, 'generation_calls') else 0,
            "total_tokens": getattr(self.generator, 'total_tokens_used', 0),
            "total_cost": getattr(self.generator, 'total_cost', 0.0)
        }


def create_pipeline(strategy: str = "v1") -> RAGPipeline:
    """
    Factory function to create a RAG Pipeline

    Args:
        strategy: Prompt strategy (v1, v2, v3, v4)

    Returns:
        Initialized RAGPipeline instance
    """
    return RAGPipeline(strategy=strategy)


# Example usage
if __name__ == "__main__":
    # Initialize pipeline
    pipeline = RAGPipeline(strategy="v1")

    # Example query
    question = "What role do youth play in political movements?"
    result = pipeline.query(question)

    print("\n" + "=" * 60)
    print("RAG PIPELINE RESULT")
    print("=" * 60)
    print(f"Question: {result['question']}")
    print(f"Strategy: {result['strategy']}")
    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Retrieved Chunks: {result['retrieved_chunks']}")
        print(f"\nAnswer:\n{result['answer']}")

    # Display statistics
    stats = pipeline.get_statistics()
    print("\n" + "=" * 60)
    print("PIPELINE STATISTICS")
    print("=" * 60)
    print(f"Total Tokens Used: {stats['total_tokens']}")
    print(f"Total Cost: ${stats['total_cost']:.6f}")
    print("=" * 60)
