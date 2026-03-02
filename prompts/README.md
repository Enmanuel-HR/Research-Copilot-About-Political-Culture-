# Prompt Templates

This directory contains prompt templates for each of the 4 distinct prompt engineering strategies used by Research Copilot.

## Files

### v1_clear_instructions.txt
**Strategy V1: Clear Instructions with Delimiters**

- **Purpose**: Fast, cost-effective responses to factual questions
- **Best For**: Quick lookups, simple questions
- **Avg Response Time**: 2-3 seconds
- **Avg Cost**: ~$0.015 per query
- **Key Features**:
  - Direct instructions with clear delimiters
  - No structured output requirements
  - Minimal prompt overhead
  - Prevents hallucination with explicit boundaries

### v2_json_output.txt
**Strategy V2: Structured JSON Output**

- **Purpose**: Machine-readable, programmatic integration
- **Best For**: API endpoints, system integration, dashboards
- **Avg Response Time**: 3-4 seconds
- **Avg Cost**: ~$0.025 per query
- **Key Features**:
  - JSON-formatted responses
  - Explicit confidence scores
  - Structured citations
  - Suitable for automation

### v3_few_shot_learning.txt
**Strategy V3: Few-Shot Learning with Examples**

- **Purpose**: Publication-quality, consistent formatting
- **Best For**: Academic writing, reports, documentation
- **Avg Response Time**: 3-4 seconds
- **Avg Cost**: ~$0.024 per query
- **Key Features**:
  - Teaches through examples
  - Natural narrative flow
  - High citation quality
  - Comprehensive answers (200-400 words)

### v4_chain_of_thought.txt
**Strategy V4: Chain-of-Thought Reasoning**

- **Purpose**: Complex reasoning, multi-step analysis
- **Best For**: Analytical questions, synthesis, comparative analysis
- **Avg Response Time**: 4-5 seconds
- **Avg Cost**: ~$0.029 per query
- **Key Features**:
  - Step-by-step reasoning displayed
  - Logical flow and connections
  - Limitations explicitly noted
  - Transparent thought process

## How to Use

### In Python Code
```python
from src.generation import RAGGenerator

# Initialize with specific strategy
generator = RAGGenerator(strategy="v3")

# Generate answer
answer = generator.generate(question, context)
```

### Direct Template Usage
1. Load template file
2. Replace `[RETRIEVED_CHUNKS]` with actual chunks
3. Replace `[USER_QUESTION]` with actual question
4. Send to OpenAI API with proper instructions

## Strategy Selection Guide

| Question Type | Recommended Strategy | Reason |
|---|---|---|
| "When was X published?" | V1 | Simple recall |
| "What does Y paper say about Z?" | V1 | Direct lookup |
| "List all authors of paper X" | V1 | Factual retrieval |
| "Compare X and Y" | V4 | Requires analysis |
| "What is the relationship between X and Y?" | V3 or V4 | Requires synthesis |
| "Explain how X influences Y" | V4 | Complex reasoning |
| "Summarize findings on topic X" | V3 | Publication quality |
| "For API integration" | V2 | Structured output |

## Prompt Engineering Best Practices

### What Works
✓ Clear, explicit instructions
✓ Specific boundaries and constraints
✓ Examples for few-shot learning
✓ Step-by-step reasoning requests
✓ Explicit citation requirements

### What to Avoid
✗ Vague or ambiguous instructions
✗ Unstructured free-form prompts
✗ No citation guidance
✗ Unlimited context allowance
✗ No hallucination prevention measures

## Customization

To modify templates:

1. **Adjust Specificity**: Make instructions more/less detailed
2. **Change Output Format**: Modify expected structure
3. **Adjust Length**: Request shorter/longer answers
4. **Add Examples**: Include more few-shot examples
5. **Modify Constraints**: Add field-specific requirements

## Performance Notes

- V1 is fastest and cheapest - use when possible
- V2 adds ~$0.010 cost for structured output
- V3 adds ~$0.009 cost for narrative quality
- V4 adds ~$0.014 cost for reasoning depth

## Citation Requirement

All strategies must include citations in the following format:
```
Author(s) (Year). "Paper Title." Journal/Conference, Volume(Issue), pages.
```

Example:
```
Aguilera, O. (2010). Cultura política y política de las culturas juveniles.
Youth Studies Review, 5(2), 45-67.
```

---

**Last Updated**: February 28, 2026
**Status**: Production Ready
