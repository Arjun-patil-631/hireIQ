# HireIQ Rubrics

Rubrics are external YAML files. The application validates that criteria weights total 100 and that each criterion has scoring levels before a rubric is used or saved.

The evaluator prompt includes the rubric, question, examples, transcript, and supplementary NLP signals. The LLM response is then validated with the Pydantic `EvaluationResult` schema before persistence.
