import json
from typing import Any

from app.ai.prompts import SYSTEM_PROMPT, build_prompt
from app.ai.rubric import calculate_overall_score, calculate_recommendation, load_rubric
from app.config import settings
from app.schemas import EvaluationResult


def _mock_evaluation(transcript: str, confidence: float, sentiment: str, question_type: str, rubric: dict | None = None) -> EvaluationResult:
    if rubric is None:
        rubric = load_rubric("technical" if question_type != "behavioral" else "behavioral")
    words = max(1, len(transcript.split()))
    has_reasoning = any(k in transcript.lower() for k in ["because", "therefore", "trade-off", "complexity", "example"])
    has_keywords = any(k in transcript.lower() for k in ["python", "sql", "api", "database", "model", "algorithm"])
    base = 70 + min(15, words / 20) + (8 if has_reasoning else 0) + (5 if has_keywords else 0)
    base = max(0, min(96, base))
    technical = base
    problem = min(100, base + (5 if has_reasoning else -4))
    communication = min(100, 68 + min(20, words / 25) - (10 if words < 20 else 0))
    confidence_bounded = max(0.0, min(100.0, float(confidence)))

    scores = {
        "technical_score": float(technical),
        "problem_solving_score": float(problem),
        "communication_score": float(communication),
        "confidence_score": confidence_bounded,
    }
    overall = calculate_overall_score(rubric, scores)
    recommendation = calculate_recommendation(rubric, overall)
    return EvaluationResult(
        technical_score=round(technical, 1),
        problem_solving_score=round(problem, 1),
        communication_score=round(communication, 1),
        confidence_score=round(confidence_bounded, 1),
        overall_score=overall,
        sentiment=sentiment if sentiment in {"positive", "neutral", "negative"} else "neutral",
        strengths=["Answer contains relevant technical vocabulary.", "Response provides a usable explanation."],
        improvements=["Add a concrete example or trade-off.", "State the reasoning steps more explicitly."],
        rationale="Demo fallback evaluation based on transcript evidence and the configured scoring dimensions. Replace with a live Gemini key for real model scoring.",
        recommendation=recommendation,
    )


def evaluate_answer(question: str, question_type: str, transcript: str, nlp: dict, rubric_name: str = "technical") -> tuple[EvaluationResult, str]:
    rubric = load_rubric(rubric_name)
    if settings.ai_provider == "mock" or not settings.gemini_api_key:
        if settings.demo_ai_fallback:
            return _mock_evaluation(transcript, float(nlp.get("confidence_score", 70)), nlp.get("sentiment", "neutral"), question_type, rubric), "demo-fallback"
        raise RuntimeError("GEMINI_API_KEY is missing and demo_ai_fallback is disabled")

    try:
        from google import genai
        from google.genai import types
    except Exception as exc:
        if settings.demo_ai_fallback:
            return _mock_evaluation(transcript, float(nlp.get("confidence_score", 70)), nlp.get("sentiment", "neutral"), question_type, rubric), "demo-fallback-sdk"
        raise RuntimeError("google-genai is not installed") from exc

    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = build_prompt(question, question_type, transcript, rubric, nlp)
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=[
            types.Content(role="user", parts=[types.Part.from_text(text=SYSTEM_PROMPT + "\n\n" + prompt)])
        ],
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
            response_schema=EvaluationResult,
        ),
    )

    raw = response.text or ""
    # Parse JSON through Pydantic. This is the gate before database storage.
    try:
        result = EvaluationResult.model_validate_json(raw)
    except Exception:
        data: Any = json.loads(raw)
        result = EvaluationResult.model_validate(data)

    # Normalize overall score and recommendation deterministically via rubric YAML
    normalized_scores = {
        "technical_score": result.technical_score,
        "problem_solving_score": result.problem_solving_score,
        "communication_score": result.communication_score,
        "confidence_score": result.confidence_score,
    }
    calculated_overall = calculate_overall_score(rubric, normalized_scores)
    calculated_rec = calculate_recommendation(rubric, calculated_overall)
    result = result.model_copy(update={"overall_score": calculated_overall, "recommendation": calculated_rec})

    return result, settings.gemini_model

