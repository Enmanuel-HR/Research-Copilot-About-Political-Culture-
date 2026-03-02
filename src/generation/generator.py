"""
LLM Generation Module

Handles answer generation using OpenAI GPT-4 with various prompt strategies.
"""

from openai import OpenAI
from typing import Dict, Any, Optional, List, Tuple
from loguru import logger
from .prompt_strategies import PromptEngineer, PromptStrategy, create_prompt


class RAGGenerator:
    """
    Generates answers using GPT-4 based on retrieved context.

    Supports multiple prompt engineering strategies and includes
    cost tracking and token management.
    """

    def __init__(
        self,
        model: str = "gpt-4",
        strategy: str = "clear_instructions",
        temperature: float = 0.5
    ):
        """
        Initialize RAG generator.

        Args:
            model: OpenAI model name (gpt-4, gpt-4-turbo, etc.)
            strategy: Prompt strategy to use
            temperature: Sampling temperature (0-1)
        """
        self.client = OpenAI()
        self.model = model
        self.strategy = strategy
        self.temperature = temperature

        # Cost tracking (GPT-4 pricing as of Feb 2026)
        self.cost_per_1k_prompt_tokens = 0.03  # $0.03 per 1K prompt tokens
        self.cost_per_1k_completion_tokens = 0.06  # $0.06 per 1K completion tokens

        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
        self.generation_calls = 0

        logger.info(
            f"RAGGenerator initialized: model={model}, "
            f"strategy={strategy}, temperature={temperature}"
        )

    def generate(
        self,
        question: str,
        context: str,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Generate answer based on question and context.

        Args:
            question: User question
            context: Retrieved document context
            max_tokens: Maximum tokens in response

        Returns:
            Dictionary with answer, usage info, and metadata
        """
        # Create prompt based on strategy
        prompt = create_prompt(self.strategy, context, question)

        try:
            # Call GPT-4
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are Research Copilot, an expert academic assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=max_tokens
            )

            # Extract response
            answer = response.choices[0].message.content

            # Track usage
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens

            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            self.generation_calls += 1

            # Calculate cost
            prompt_cost = (prompt_tokens / 1000) * self.cost_per_1k_prompt_tokens
            completion_cost = (completion_tokens / 1000) * self.cost_per_1k_completion_tokens
            call_cost = prompt_cost + completion_cost
            self.total_cost += call_cost

            logger.info(
                f"Generated answer ({prompt_tokens} prompt + {completion_tokens} completion tokens). "
                f"Cost: ${call_cost:.6f}"
            )

            return {
                "answer": answer,
                "question": question,
                "strategy": self.strategy,
                "model": self.model,
                "tokens": {
                    "prompt": prompt_tokens,
                    "completion": completion_tokens,
                    "total": prompt_tokens + completion_tokens
                },
                "cost": call_cost
            }

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

    def generate_batch(
        self,
        questions: List[str],
        contexts: List[str],
        max_tokens: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Generate answers for multiple question-context pairs.

        Args:
            questions: List of questions
            contexts: List of contexts (same length as questions)
            max_tokens: Maximum tokens per response

        Returns:
            List of generation results
        """
        if len(questions) != len(contexts):
            raise ValueError("Questions and contexts must have same length")

        results = []
        for question, context in zip(questions, contexts):
            result = self.generate(question, context, max_tokens)
            results.append(result)

        return results

    def change_strategy(self, strategy: str) -> None:
        """
        Change the prompt strategy.

        Args:
            strategy: New strategy name
        """
        self.strategy = strategy
        logger.info(f"Prompt strategy changed to: {strategy}")

    def get_cost_report(self) -> Dict[str, Any]:
        """
        Get cost report for all generations.

        Returns:
            Dictionary with cost information
        """
        return {
            "model": self.model,
            "total_calls": self.generation_calls,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "total_cost": self.total_cost,
            "avg_cost_per_call": self.total_cost / self.generation_calls if self.generation_calls > 0 else 0,
            "avg_tokens_per_call": (self.total_prompt_tokens + self.total_completion_tokens) / self.generation_calls
                                   if self.generation_calls > 0 else 0,
        }

    def print_cost_report(self) -> None:
        """Print formatted cost report."""
        report = self.get_cost_report()

        print("\n" + "=" * 70)
        print("GENERATION COST REPORT")
        print("=" * 70)
        print(f"Model: {report['model']}")
        print(f"Total API Calls: {report['total_calls']}")
        print(f"Total Tokens: {report['total_tokens']:,}")
        print(f"  - Prompt: {report['total_prompt_tokens']:,}")
        print(f"  - Completion: {report['total_completion_tokens']:,}")
        print(f"Avg Tokens per Call: {report['avg_tokens_per_call']:.1f}")
        print(f"Total Cost: ${report['total_cost']:.6f}")
        print(f"Avg Cost per Call: ${report['avg_cost_per_call']:.6f}")
        print("=" * 70 + "\n")


def create_generator(
    model: str = "gpt-4",
    strategy: str = "clear_instructions",
    temperature: float = 0.5
) -> RAGGenerator:
    """
    Factory function to create a RAG generator.

    Args:
        model: OpenAI model name
        strategy: Prompt strategy
        temperature: Sampling temperature

    Returns:
        Configured RAGGenerator instance
    """
    return RAGGenerator(model, strategy, temperature)
