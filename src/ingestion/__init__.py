"""
Ingestion module for PDF processing and text extraction.
"""

from .pdf_extractor import extract_text_from_pdf, extract_from_multiple_pdfs
from .text_cleaner import (
    clean_extracted_text,
    preprocess_text,
    remove_page_markers,
    split_into_sections,
    clean_paragraph,
    normalize_whitespace
)

__all__ = [
    "extract_text_from_pdf",
    "extract_from_multiple_pdfs",
    "clean_extracted_text",
    "preprocess_text",
    "remove_page_markers",
    "split_into_sections",
    "clean_paragraph",
    "normalize_whitespace",
]
