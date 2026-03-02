"""
Evaluation Script for Research Copilot
Runs the evaluation question set against the RAG system and tracks metrics
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieval import RAGRetriever
from src.generation import RAGGenerator
from src.embedding import OpenAIEmbedder


class CopilotEvaluator:
    """Evaluates Research Copilot performance on test questions"""

    def __init__(self, questions_file: str = "eval/questions.json"):
        """Initialize evaluator with questions"""
        self.questions_file = questions_file
        self.results = {
            "evaluation_date": datetime.now().isoformat(),
            "total_questions": 0,
            "results_by_category": {},
            "strategy_comparison": {},
            "overall_metrics": {}
        }
        self.load_questions()

    def load_questions(self):
        """Load evaluation questions from JSON"""
        with open(self.questions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.questions = data
        self.total_questions = data['evaluation_framework']['total_questions']
        print(f"Loaded {self.total_questions} evaluation questions")

    def evaluate_question(self, question: str, strategy: str = "v1") -> dict:
        """
        Evaluate a single question with specified strategy

        Args:
            question: The question to evaluate
            strategy: Prompt strategy to use (v1, v2, v3, v4)

        Returns:
            Dictionary with evaluation results
        """
        start_time = time.time()

        try:
            # Initialize RAG components (in production, these would be cached)
            retriever = RAGRetriever()
            generator = RAGGenerator(strategy=strategy)

            # Retrieve relevant chunks
            retrieved = retriever.retrieve(question, k=5)

            # Generate answer
            answer = generator.generate(question, retrieved)

            # Calculate metrics
            response_time = time.time() - start_time

            result = {
                "question": question,
                "strategy": strategy,
                "response_time": response_time,
                "answer": answer,
                "retrieved_chunks": len(retrieved),
                "status": "success"
            }

        except Exception as e:
            result = {
                "question": question,
                "strategy": strategy,
                "error": str(e),
                "status": "error"
            }

        return result

    def run_evaluation(self, strategies: list = None, sample_size: int = None):
        """
        Run full evaluation suite

        Args:
            strategies: List of strategies to test (default: all)
            sample_size: Number of questions to test (default: all)
        """
        if strategies is None:
            strategies = ["v1", "v2", "v3", "v4"]

        # Get all questions from all categories
        all_questions = []
        for category_key in ["factual_questions", "analytical_questions",
                            "synthesis_questions", "edge_cases"]:
            if category_key in self.questions:
                category = self.questions[category_key]
                if "questions" in category:
                    all_questions.extend(category["questions"])

        if sample_size:
            all_questions = all_questions[:sample_size]

        print(f"\nRunning evaluation on {len(all_questions)} questions")
        print(f"Strategies: {strategies}")
        print("-" * 60)

        for i, q in enumerate(all_questions, 1):
            question_text = q["question"]
            category = q["category"]
            difficulty = q.get("difficulty", "unknown")

            print(f"\n[{i}/{len(all_questions)}] {category.upper()} - {difficulty}")
            print(f"Q: {question_text[:80]}...")

            # Test with each strategy
            for strategy in strategies:
                print(f"  Testing with {strategy}...", end=" ", flush=True)
                result = self.evaluate_question(question_text, strategy)

                if result["status"] == "success":
                    time_ms = result["response_time"] * 1000
                    print(f"OK ({time_ms:.0f}ms)")
                else:
                    print(f"ERROR: {result.get('error', 'Unknown')}")

    def generate_report(self, output_file: str = "eval/results/evaluation_report.json"):
        """Generate and save evaluation report"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\nEvaluation report saved to: {output_path}")

    def display_summary(self):
        """Display evaluation summary"""
        print("\n" + "=" * 60)
        print("EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Total Questions: {self.total_questions}")
        print(f"Evaluation Date: {self.results['evaluation_date']}")
        print("\nCategories:")
        print("  - Factual Questions: 7")
        print("  - Analytical Questions: 7")
        print("  - Synthesis Questions: 3")
        print("  - Edge Cases: 2")
        print("\nStrategies:")
        print("  - V1: Clear Instructions (fastest)")
        print("  - V2: Structured JSON (API-ready)")
        print("  - V3: Few-Shot Learning (quality)")
        print("  - V4: Chain-of-Thought (reasoning)")


def main():
    """Run evaluation"""
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate Research Copilot")
    parser.add_argument("--strategy", type=str, help="Specific strategy to test")
    parser.add_argument("--sample", type=int, help="Number of questions to test")
    parser.add_argument("--question", type=str, help="Specific question to test")

    args = parser.parse_args()

    # Initialize evaluator
    evaluator = CopilotEvaluator()

    if args.question:
        # Test single question
        result = evaluator.evaluate_question(args.question, args.strategy or "v1")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # Run full evaluation
        strategies = [args.strategy] if args.strategy else ["v1", "v3", "v4"]
        evaluator.run_evaluation(strategies=strategies, sample_size=args.sample)
        evaluator.generate_report()
        evaluator.display_summary()


if __name__ == "__main__":
    main()
