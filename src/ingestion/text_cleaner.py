"""
Text Cleaning Module

Handles common PDF extraction issues and text normalization.
"""

import re
from typing import List
from loguru import logger


def clean_extracted_text(text: str) -> str:
    """
    Clean and normalize extracted PDF text.

    Args:
        text: Raw extracted text from PDF

    Returns:
        Cleaned and normalized text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)

    # Fix hyphenated words at line breaks
    text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)

    # Remove page numbers and headers (customize per document)
    text = re.sub(r'\n\d+\n', '\n', text)

    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")

    # Remove repeated newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Fix common OCR errors
    text = re.sub(r'\b(tl\w+)\b', lambda m: m.group(1).replace('tl', 'th'), text)

    return text.strip()


def remove_page_markers(text: str) -> str:
    """
    Remove page markers from text.

    Args:
        text: Text with page markers like [PAGE 1]

    Returns:
        Text without page markers
    """
    return re.sub(r'\[PAGE \d+\]', '', text)


def split_into_sections(text: str) -> List[str]:
    """
    Split text into sections based on common academic paper structure.

    Args:
        text: Full document text

    Returns:
        List of text sections
    """
    sections = []
    current_section = ""

    # Common academic section headers
    section_pattern = r'^(ABSTRACT|INTRODUCTION|LITERATURE REVIEW|METHODOLOGY|RESULTS|DISCUSSION|CONCLUSION|REFERENCES)\s*'

    for line in text.split('\n'):
        if re.match(section_pattern, line.upper()):
            if current_section.strip():
                sections.append(current_section.strip())
            current_section = line
        else:
            current_section += '\n' + line

    if current_section.strip():
        sections.append(current_section.strip())

    return sections


def clean_paragraph(paragraph: str) -> str:
    """
    Clean a single paragraph.

    Args:
        paragraph: Text paragraph

    Returns:
        Cleaned paragraph
    """
    # Remove leading/trailing whitespace
    paragraph = paragraph.strip()

    # Remove URLs
    paragraph = re.sub(r'http\S+|www\S+', '', paragraph)

    # Remove email addresses
    paragraph = re.sub(r'\S+@\S+', '', paragraph)

    # Remove citation brackets [1], [Smith et al., 2020], etc
    paragraph = re.sub(r'\[\d+\]', '', paragraph)
    paragraph = re.sub(r'\[[^\]]+et al\.[^\]]*\]', '', paragraph)

    # Fix spacing around punctuation
    paragraph = re.sub(r'\s+([.,!?;:])', r'\1', paragraph)

    return paragraph


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace while preserving paragraph structure.

    Args:
        text: Text with irregular whitespace

    Returns:
        Text with normalized whitespace
    """
    # Preserve double newlines (paragraph breaks)
    parts = text.split('\n\n')
    cleaned_parts = []

    for part in parts:
        # Remove extra spaces within paragraphs
        cleaned = ' '.join(part.split())
        cleaned_parts.append(cleaned)

    return '\n\n'.join(cleaned_parts)


def preprocess_text(text: str, remove_citations: bool = False) -> str:
    """
    Complete preprocessing pipeline for extracted PDF text.

    Args:
        text: Raw extracted text
        remove_citations: Whether to remove academic citations

    Returns:
        Fully preprocessed text
    """
    # Apply cleaning functions in sequence
    text = clean_extracted_text(text)
    text = remove_page_markers(text)
    text = normalize_whitespace(text)

    if remove_citations:
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\([A-Z][a-z]+\s+et\s+al\.?,?\s*\d{4}\)', '', text)

    logger.info(f"Text preprocessing completed: {len(text)} characters")

    return text
