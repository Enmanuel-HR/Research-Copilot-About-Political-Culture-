"""
Configuration module for Research Copilot
Loads environment variables from .env file
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate API key is loaded
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not found in .env file. "
        "Please create a .env file with your API key. "
        "You can use .env.example as a template."
    )

# Project Paths
PROJECT_ROOT = Path(__file__).parent
LECTURAS_DIR = PROJECT_ROOT / "lecturas"
PAPERS_DIR = PROJECT_ROOT / "papers"
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_DB_DIR = PROJECT_ROOT / "chroma_data"

# Create necessary directories
for directory in [PAPERS_DIR, DATA_DIR, CHROMA_DB_DIR]:
    directory.mkdir(exist_ok=True)

# OpenAI Configuration
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# ChromaDB Configuration
CHROMA_COLLECTION_NAME = "political_culture_papers"
CHROMA_PERSIST_DIRECTORY = str(CHROMA_DB_DIR)

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

__all__ = [
    "OPENAI_API_KEY",
    "PROJECT_ROOT",
    "LECTURAS_DIR",
    "PAPERS_DIR",
    "DATA_DIR",
    "CHROMA_DB_DIR",
    "EMBEDDING_MODEL",
    "CHAT_MODEL",
    "CHUNK_SIZE",
    "CHUNK_OVERLAP",
    "CHROMA_COLLECTION_NAME",
    "CHROMA_PERSIST_DIRECTORY",
    "LOG_LEVEL",
]
