# Evaluation Framework

This directory contains the evaluation framework for Research Copilot, including test questions, evaluation scripts, and results documentation.

## Structure

```
eval/
├── README.md                    # This file
├── questions.json              # Comprehensive evaluation questions
├── evaluate.py                 # Evaluation script
└── results/                    # Evaluation results directory
    ├── evaluation_report.json  # Main results
    ├── strategy_comparison.json # Strategy comparison
    └── metrics.json            # Detailed metrics
```

## Question Categories

### 1. Factual Questions (7 questions)
Tests the system's ability to recall specific information from papers.

- What is the main contribution of specific papers?
- Author and title identification
- Publication dates
- Case studies and geographic focus
- Discipline identification
- Historical periods

**Expected Strategy**: V1 (Clear Instructions)
**Expected Performance**: High accuracy (>95%)

### 2. Analytical Questions (8 questions)
Tests the system's understanding and analysis capabilities.

- Methodology recommendations
- Critical perspective limitations
- Evidence evaluation
- Historical evolution analysis
- Variable identification
- Relationship analysis
- Synthesis of concepts

**Expected Strategy**: V3-V4 (Few-Shot or Chain-of-Thought)
**Expected Performance**: Comprehensive, well-reasoned responses

### 3. Synthesis Questions (3 questions)
Tests the system's ability to integrate information across papers.

- Common themes identification
- Evolution of field
- Research gaps identification

**Expected Strategy**: V3-V4
**Expected Performance**: Cross-paper synthesis, 4+ citations

### 4. Edge Cases (2 questions)
Tests system robustness and hallucination prevention.

- Out-of-domain questions
- Non-existent sources

**Expected Response**: "Not covered in provided papers"
**Expected Strategy**: V1
**Expected Performance**: No hallucination

## Running Evaluations

### Quick Test
```bash
# Test single question with specific strategy
python eval/evaluate.py --question "What role do youth play in political movements?" --strategy v3
```

### Full Evaluation
```bash
# Run all questions with multiple strategies
python eval/evaluate.py
```

### Sample Evaluation
```bash
# Test only first 5 questions
python eval/evaluate.py --sample 5
```

### Specific Strategy
```bash
# Test only V1 strategy
python eval/evaluate.py --strategy v1
```

## Evaluation Metrics

### 1. Citation Accuracy (20% weight)
- Are citations accurate?
- Is APA format correct?
- Are sources properly referenced?
- **Target**: >95%

### 2. Answer Relevance (20% weight)
- Does answer address the question?
- Is information pertinent?
- Is scope appropriate?
- **Target**: 4.0/5.0

### 3. Hallucination Rate (20% weight)
- Does answer cite non-existent papers?
- Are claims unsupported?
- Does system acknowledge limits?
- **Target**: <2%

### 4. Completeness (15% weight)
- Is answer thorough?
- Are key points covered?
- Is depth appropriate?
- **Target**: 4.0/5.0

### 5. Response Time (15% weight)
- How fast is the response?
- Is latency acceptable?
- Varies by strategy
- **Target**: <5 seconds

### 6. Information Accuracy (10% weight)
- Are facts correct?
- Is context appropriate?
- Are nuances captured?
- **Target**: 4.5/5.0

## Strategy Evaluation

### V1: Clear Instructions
- **Expected Strength**: Speed, cost-effectiveness
- **Expected Weakness**: Limited depth
- **Use For**: Factual questions, edge cases
- **Target Score**: >85%

### V2: Structured JSON
- **Expected Strength**: Machine-readability
- **Expected Weakness**: Slightly higher cost
- **Use For**: API integration, factual queries
- **Target Score**: >80%

### V3: Few-Shot Learning
- **Expected Strength**: Answer quality, narrative flow
- **Expected Weakness**: Higher token usage
- **Use For**: Analytical questions, synthesis
- **Target Score**: >85%

### V4: Chain-of-Thought
- **Expected Strength**: Reasoning quality, transparency
- **Expected Weakness**: Highest cost and latency
- **Use For**: Complex analysis, synthesis
- **Target Score**: >90%

## Evaluation Results

Results are stored in `eval/results/` directory:

### evaluation_report.json
Main evaluation results with:
- Question-by-question responses
- Strategy comparison
- Overall metrics
- Timestamp and metadata

### strategy_comparison.json
Comparative analysis:
- Cost per strategy
- Speed metrics
- Quality scores
- Recommendation

### metrics.json
Detailed metrics:
- Citation accuracy percentages
- Response time distributions
- Hallucination rates
- Coverage analysis

## How to Interpret Results

### Good Performance Indicators
✓ Citation accuracy >95%
✓ Answer relevance 4.0+/5.0
✓ Hallucination rate <2%
✓ Response time <5 seconds
✓ Completeness 4.0+/5.0

### Areas for Improvement
✗ Low citation accuracy: Check paper indexing
✗ High hallucination: Review prompt templates
✗ Slow responses: Optimize retrieval parameters
✗ Low relevance: Improve embedding quality

## Automated Evaluation Script

The `evaluate.py` script:

1. **Loads questions** from `questions.json`
2. **Initializes RAG system** with all components
3. **Processes questions** through selected strategies
4. **Calculates metrics** for each response
5. **Generates report** with results
6. **Saves results** to `results/` directory

### Key Functions
- `load_questions()`: Load evaluation questions
- `evaluate_question()`: Test single question
- `run_evaluation()`: Execute full evaluation suite
- `generate_report()`: Create results report
- `display_summary()`: Show evaluation summary

## Course Assignment Context

**Course**: Basements in Prompt Engineering (Q-LAB / PUCP)
**Purpose**: Evaluate RAG system effectiveness
**Scope**: 20 questions across 4 categories
**Required Metrics**: Citation accuracy, response quality
**Submission**: Evaluation results included in final deliverables

## Future Enhancements

- [ ] Automated human evaluation scoring
- [ ] Comparative baseline testing
- [ ] User satisfaction surveys
- [ ] Error analysis dashboards
- [ ] Continuous monitoring
- [ ] A/B testing framework
- [ ] Regression testing suite
- [ ] Performance tracking over time

---

**Last Updated**: February 28, 2026
**Status**: Production Ready
**Next Review**: After YouTube video completion
