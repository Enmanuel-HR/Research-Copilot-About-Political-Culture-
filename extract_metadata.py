"""
Extract metadata from PDF papers and create paper_catalog.json
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

def extract_pdf_metadata(pdf_path: str) -> Dict:
    """Extract metadata from PDF file"""
    metadata = {
        "title": None,
        "abstract": None,
        "year": None,
        "authors": []
    }

    # Try pdfplumber first (more robust)
    if pdfplumber:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                if len(pdf.pages) > 0:
                    first_page = pdf.pages[0].extract_text()
                    if first_page and "abstract" in first_page.lower():
                        abstract_start = first_page.lower().find("abstract")
                        abstract_text = first_page[abstract_start:abstract_start+500]
                        metadata["abstract"] = abstract_text[:300]
        except Exception as e:
            pass

    # Fallback to PyPDF2
    if not metadata["abstract"] and PyPDF2:
        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                if pdf_reader.metadata:
                    metadata["title"] = pdf_reader.metadata.get("/Title")
                if len(pdf_reader.pages) > 0:
                    first_page = pdf_reader.pages[0].extract_text()
                    if first_page and "abstract" in first_page.lower():
                        abstract_start = first_page.lower().find("abstract")
                        abstract_text = first_page[abstract_start:abstract_start+500]
                        metadata["abstract"] = abstract_text[:300]
        except Exception as e:
            pass

    return metadata

def parse_filename(filename: str) -> Dict:
    """Parse filename to extract metadata"""
    # Remove .pdf extension
    name = filename.replace(".pdf", "")

    info = {
        "authors": [],
        "year": None,
        "title": name
    }

    # Try to extract year (4 consecutive digits in parentheses)
    year_match = re.search(r'\((\d{4})\)', name)
    if year_match:
        info["year"] = int(year_match.group(1))
        # Extract author(s) and title around year
        parts = name.split(f"({year_match.group(1)})")
        if len(parts) > 0:
            authors_part = parts[0].strip()
            info["authors"] = [a.strip() for a in authors_part.split(",")][:3]
            if len(parts) > 1:
                info["title"] = parts[1].strip()

    return info

def create_paper_catalog(lectures_dir: str, output_file: str):
    """Create paper catalog JSON from PDFs in directory"""

    papers = []
    paper_files = sorted([f for f in os.listdir(lectures_dir) if f.endswith('.pdf')])

    for idx, filename in enumerate(paper_files, 1):
        pdf_path = os.path.join(lectures_dir, filename)

        # Parse filename
        parsed = parse_filename(filename)

        # Extract PDF metadata
        pdf_metadata = extract_pdf_metadata(pdf_path)

        paper = {
            "id": f"paper_{idx:03d}",
            "title": pdf_metadata["title"] or parsed["title"],
            "authors": parsed["authors"],
            "year": parsed["year"],
            "venue": None,  # Will be populated manually if needed
            "doi": None,    # Will be populated manually if needed
            "filename": filename,
            "filepath": pdf_path,
            "topics": [],  # To be populated during RAG setup
            "abstract": pdf_metadata["abstract"]
        }

        papers.append(paper)
        print(f"Processed {idx}: {paper['title'][:60]}...")

    # Create catalog structure
    catalog = {
        "metadata": {
            "total_papers": len(papers),
            "created": str(Path(output_file).parent),
            "source_directory": lectures_dir
        },
        "papers": papers
    }

    # Save to JSON
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Catalog created with {len(papers)} papers at {output_file}")
    return catalog

if __name__ == "__main__":
    lecturas_dir = r"C:\Users\USUARIO\Research_Copilot_1\lecturas"
    output_file = r"C:\Users\USUARIO\Research_Copilot_1\papers\paper_catalog.json"

    create_paper_catalog(lecturas_dir, output_file)
