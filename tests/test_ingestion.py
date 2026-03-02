"""
Unit tests for document ingestion module
Tests PDF extraction and text cleaning functionality
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import extract_text_from_pdf, preprocess_text


class TestPDFExtraction:
    """Test PDF text extraction"""

    def test_extract_text_from_valid_pdf(self):
        """Test extracting text from a valid PDF file"""
        pdf_path = "lecturas/"
        pdf_files = list(Path(pdf_path).glob("*.pdf"))

        if pdf_files:
            result = extract_text_from_pdf(str(pdf_files[0]))
            assert result is not None
            assert "text" in result
            assert len(result["text"]) > 0
            assert "metadata" in result

    def test_extract_returns_metadata(self):
        """Test that extraction returns metadata"""
        pdf_path = "lecturas/"
        pdf_files = list(Path(pdf_path).glob("*.pdf"))

        if pdf_files:
            result = extract_text_from_pdf(str(pdf_files[0]))
            assert "total_pages" in result
            assert result["total_pages"] > 0

    def test_extract_handles_missing_file(self):
        """Test that extraction fails gracefully for missing files"""
        with pytest.raises(Exception):
            extract_text_from_pdf("nonexistent_file.pdf")


class TestTextCleaning:
    """Test text cleaning and preprocessing"""

    def test_clean_text_removes_extra_whitespace(self):
        """Test that cleaning removes extra whitespace"""
        dirty_text = "This  is   a\n\n\ntest"
        clean_text = preprocess_text(dirty_text)
        assert "\n\n" not in clean_text
        assert "  " not in clean_text

    def test_clean_text_preserves_content(self):
        """Test that cleaning preserves actual content"""
        text = "Political Culture and Social Movements in Peru"
        clean_text = preprocess_text(text)
        assert "Political Culture" in clean_text
        assert "Peru" in clean_text

    def test_clean_text_handles_empty_input(self):
        """Test that cleaning handles empty input"""
        clean_text = preprocess_text("")
        assert isinstance(clean_text, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
