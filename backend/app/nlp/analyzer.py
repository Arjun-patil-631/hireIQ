import re
from collections import Counter

FILLERS = {"um", "uh", "like", "actually", "basically", "you know", "sort of", "kind of"}
STOPWORDS = {
    "the", "and", "a", "to", "of", "in", "is", "it", "for", "on", "that", "this", "with", "as", "are",
    "was", "were", "be", "by", "or", "an", "at", "from", "we", "i", "you", "they", "he", "she", "my",
    "our", "their", "but", "if", "then", "so", "can", "will", "would", "should", "have", "has", "had",
}


def analyze_text(text: str) -> dict:
    lowered = text.lower()
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        compound = float(SentimentIntensityAnalyzer().polarity_scores(text)["compound"])
    except Exception:
        positive_words = {"good", "clear", "effective", "success", "strong", "improve", "reliable"}
        negative_words = {"bad", "wrong", "fail", "failed", "problem", "issue", "confusing"}
        tokens = re.findall(r"[a-zA-Z']+", lowered)
        compound = (sum(t in positive_words for t in tokens) - sum(t in negative_words for t in tokens)) / max(1, len(tokens))

    if compound >= 0.05:
        sentiment = "positive"
    elif compound <= -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    # spaCy is required by the brief; gracefully degrade if the language model is unavailable.
    keywords: list[str] = []
    entities: list[str] = []
    try:
        import spacy

        try:
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text)
            entities = sorted({ent.text.strip() for ent in doc.ents if ent.text.strip()})[:12]
            candidates = [t.lemma_.lower() for t in doc if t.is_alpha and not t.is_stop and len(t) > 3]
            counts = Counter(candidates)
            keywords = [word for word, _ in counts.most_common(12)]
        except Exception:
            nlp = spacy.blank("en")
            doc = nlp(text)
            tokens = [t.text.lower() for t in doc if t.text.isalpha() and t.text.lower() not in STOPWORDS and len(t.text) > 3]
            keywords = [w for w, _ in Counter(tokens).most_common(12)]
    except Exception:
        tokens = re.findall(r"[a-zA-Z]{4,}", lowered)
        keywords = [w for w, _ in Counter(t for t in tokens if t not in STOPWORDS).most_common(12)]

    tokens = re.findall(r"[a-zA-Z']+", lowered)
    filler_hits = 0
    for filler in FILLERS:
        filler_hits += len(re.findall(rf"\b{re.escape(filler)}\b", lowered))
    filler_ratio = min(1.0, filler_hits / max(1, len(tokens)))

    # Supplementary confidence heuristic. It deliberately does not use demographic or identity signals.
    sentence_count = max(1, len(re.split(r"[.!?]+", text)) - 1)
    avg_sentence_words = len(tokens) / sentence_count
    confidence = 78.0
    confidence -= min(18.0, filler_ratio * 180)
    confidence += min(12.0, max(0.0, avg_sentence_words - 8) * 0.7)
    confidence = max(35.0, min(96.0, confidence))

    return {
        "keywords": keywords,
        "entities": entities,
        "sentiment": sentiment,
        "sentiment_compound": round(compound, 3),
        "confidence_score": round(confidence, 1),
        "filler_ratio": round(filler_ratio, 4),
    }
