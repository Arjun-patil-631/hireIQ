SYSTEM_PROMPT = """
You are HireIQ's interview evaluation engine. Evaluate a candidate's answer ONLY against the
question and rubric supplied. Return the requested structured JSON.

Fairness and safety requirements:
- Never score, infer, or mention demographic traits such as race, ethnicity, nationality, religion,
  gender, age, disability, health status, socioeconomic background, appearance, or name.
- Do not reward or penalize accent, dialect, or speech style unless the configured rubric explicitly
  and job-relevantly evaluates communication clarity. Never treat accent as a competence signal.
- Do not infer personality or protected characteristics from a transcript.
- Base scores on evidence in the answer: correctness, reasoning, relevance, clarity, and the rubric.
- Confidence is a supplementary signal and must not dominate competence scoring.
- Quote short evidence from the transcript only when helpful.
- If the transcript lacks evidence for a criterion, say so rather than inventing evidence.
""".strip()


def build_prompt(question: str, question_type: str, transcript: str, rubric: dict, nlp: dict) -> str:
    criteria = rubric.get("criteria", [])
    criterion_lines = []
    for c in criteria:
        criterion_lines.append(
            f"- {c['name']} ({c['weight']}%): {c['description']}\n"
            f"  Excellent: {c.get('levels', {}).get('excellent', '')}\n"
            f"  Good: {c.get('levels', {}).get('good', '')}\n"
            f"  Needs work: {c.get('levels', {}).get('needs_improvement', '')}"
        )
    examples = rubric.get("examples", {})
    return f"""
Question type: {question_type}
Question: {question}

Rubric criteria:
{chr(10).join(criterion_lines)}

Strong-answer example:
{examples.get('strong', 'Not provided')}

Weak-answer example:
{examples.get('weak', 'Not provided')}

Candidate transcript:
{transcript}

Supporting NLP signals (use only as context, not as a proxy for competence):
- keywords: {', '.join(nlp.get('keywords', []))}
- entities: {', '.join(nlp.get('entities', []))}
- sentiment: {nlp.get('sentiment', 'neutral')} ({nlp.get('sentiment_compound', 0):.3f})
- confidence heuristic: {nlp.get('confidence_score', 70):.1f}/100

Return:
- technical_score 0-100
- problem_solving_score 0-100
- communication_score 0-100
- confidence_score 0-100
- overall_score 0-100
- sentiment: positive | neutral | negative
- strengths: 2-5 concise evidence-based items
- improvements: 2-5 concise evidence-based items
- rationale: concise explanation grounded in the transcript
- recommendation: Proceed | Hold | Reject
""".strip()
