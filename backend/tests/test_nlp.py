from app.nlp.analyzer import analyze_text


def test_nlp_output_bounds():
    result = analyze_text("Python and SQL are useful for building reliable APIs because the design is testable.")
    assert 0 <= result["confidence_score"] <= 100
    assert result["sentiment"] in {"positive", "neutral", "negative"}
    assert isinstance(result["keywords"], list)
