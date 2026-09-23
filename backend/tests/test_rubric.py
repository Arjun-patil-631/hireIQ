from pathlib import Path

from app.ai.rubric import load_rubric, validate_rubric


def test_technical_rubric_loads():
    data = load_rubric("technical")
    assert data["criteria"]
    assert round(sum(float(c["weight"]) for c in data["criteria"]), 5) == 100


def test_bad_weight_rejected():
    try:
        validate_rubric({"criteria": [{"name": "x", "description": "y", "weight": 10, "levels": {"excellent": "z"}}]})
    except ValueError:
        return
    raise AssertionError("invalid rubric should fail")


def test_behavioral_rubric_loads():
    from app.ai.rubric import load_rubric
    data = load_rubric("behavioral")
    assert data["criteria"]
    assert round(sum(float(c["weight"]) for c in data["criteria"]), 5) == 100


def test_calculate_overall_score_and_recommendation():
    from app.ai.rubric import calculate_overall_score, calculate_recommendation, load_rubric
    rubric = load_rubric("technical")
    scores = {
        "technical_score": 80.0,
        "problem_solving_score": 70.0,
        "communication_score": 90.0,
        "confidence_score": 75.0,
    }
    overall = calculate_overall_score(rubric, scores)
    assert 0 <= overall <= 100
    rec = calculate_recommendation(rubric, overall)
    assert rec in {"Proceed", "Hold", "Reject"}
