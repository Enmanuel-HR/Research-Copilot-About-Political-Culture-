"""
Generation module for LLM response synthesis.

Implements prompt engineering strategies and GPT-4 answer generation.
"""

from .prompt_strategies import PromptEngineer, PromptStrategy, create_prompt
from .generator import RAGGenerator, create_generator

__all__ = [
    "PromptEngineer",
    "PromptStrategy",
    "create_prompt",
    "RAGGenerator",
    "create_generator",
]
