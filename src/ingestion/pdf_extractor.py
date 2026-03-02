"""
PDF Text Extraction Module

Handles extraction of text and metadata from PDF documents.
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Any
from loguru import logger


def extract_text_from_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Extract text and metadata from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        dict with keys: text, metadata, pages, total_pages, extraction_warnings
            - text: Full document text with page markers
            - metadata: PDF metadata (title, author, creation date, etc.)
            - pages: List of dicts with page-level information
            - total_pages: Total number of pages
            - extraction_warnings: List of any warnings during extraction
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    pages = []
    warnings = []
    metadata = None
    total_pages = 0

    try:
        total_pages = len(doc)
        for page_num, page in enumerate(doc):
            text = page.get_text()
            pages.append({
                "page_number": page_num + 1,
                "text": text,
                "char_count": len(text)
            })
            full_text += f"\n[PAGE {page_num + 1}]\n{text}"

        # Document metadata
        metadata = doc.metadata

    except Exception as e:
        warnings.append(f"Error during extraction: {str(e)}")
        logger.warning(f"Warning extracting {pdf_path}: {e}")

    finally:
        doc.close()

    return {
        "text": full_text,
        "metadata": metadata,
        "pages": pages,
        "total_pages": total_pages,
        "extraction_warnings": warnings
    }


def extract_from_multiple_pdfs(pdf_paths: List[str]) -> Dict[str, Any]:
    """
    Extract text from multiple PDF files.

    Args:
        pdf_paths: List of paths to PDF files

    Returns:
        dict with aggregated results from all PDFs
    """
    results = {}
    successful = 0
    failed = 0

    for pdf_path in pdf_paths:
        try:
            pdf_name = Path(pdf_path).name
            result = extract_text_from_pdf(pdf_path)
            results[pdf_name] = result
            successful += 1
            logger.info(f"Successfully extracted: {pdf_name}")
        except Exception as e:
            failed += 1
            logger.error(f"Failed to extract {pdf_path}: {e}")

    return {
        "documents": results,
        "summary": {
            "total": len(pdf_paths),
            "successful": successful,
            "failed": failed
        }
    }
