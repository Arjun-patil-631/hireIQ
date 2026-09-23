from app.ai.evaluator import _mock_evaluation


def test_mock_evaluation_is_schema_valid():
    result = _mock_evaluation("I would profile the system first because complexity matters.", 80, "positive", "technical")
    assert 0 <= result.overall_score <= 100
    assert result.recommendation in {"Proceed", "Hold", "Reject"}
