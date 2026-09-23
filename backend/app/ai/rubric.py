from pathlib import Path

import yaml

from app.config import settings


class RubricError(ValueError):
    pass


def rubric_path(name: str) -> Path:
    safe_name = name.replace("..", "_").replace("/", "_").replace("\\", "_")
    path = Path(settings.config_dir) / "rubrics" / f"{safe_name}.yaml"
    return path


def load_rubric(name: str = "technical") -> dict:
    path = rubric_path(name)
    if not path.exists():
        raise RubricError(f"Rubric '{name}' not found")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    validate_rubric(data)
    return data


def validate_rubric(data: dict) -> None:
    criteria = data.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        raise RubricError("rubric.criteria must be a non-empty list")
    weight_total = sum(float(c.get("weight", 0)) for c in criteria)
    if abs(weight_total - 100.0) > 0.01:
        raise RubricError(f"criterion weights must total 100, got {weight_total}")
    for criterion in criteria:
        if not criterion.get("name") or not criterion.get("description"):
            raise RubricError("each criterion requires name and description")
        levels = criterion.get("levels", {})
        if not levels:
            raise RubricError(f"criterion '{criterion['name']}' needs scoring levels")


def calculate_overall_score(rubric: dict, scores: dict[str, float]) -> float:
    """Calculate normalized 0-100 overall score deterministically from criteria weights."""
    criteria = rubric.get("criteria", [])
    if not criteria:
        return 0.0
    weighted_sum = 0.0
    total_weight = 0.0
    # Map common criterion name keys (case-insensitive)
    normalized_keys = {k.lower().replace(" ", "_"): v for k, v in scores.items()}
    for c in criteria:
        c_name = c["name"]
        key = c_name.lower().replace(" ", "_")
        weight = float(c.get("weight", 0))
        total_weight += weight
        # Match score by exact key, name, or substring
        score_val = scores.get(c_name)
        if score_val is None:
            score_val = normalized_keys.get(key)
        if score_val is None:
            # Fallback to general score mapping
            if "tech" in key:
                score_val = normalized_keys.get("technical_score", 70.0)
            elif "problem" in key or "action" in key:
                score_val = normalized_keys.get("problem_solving_score", 70.0)
            elif "comm" in key:
                score_val = normalized_keys.get("communication_score", 70.0)
            else:
                score_val = normalized_keys.get("confidence_score", 70.0)
        weighted_sum += float(score_val) * (weight / 100.0)
    
    overall = weighted_sum if total_weight > 0 else 0.0
    return round(max(0.0, min(100.0, overall)), 1)


def calculate_recommendation(rubric: dict, overall_score: float) -> str:
    """Determine recommendation based on thresholds configured in the rubric YAML."""
    thresholds = rubric.get("recommendation_thresholds", {})
    proceed_threshold = float(thresholds.get("proceed", 75))
    hold_threshold = float(thresholds.get("hold", 55))
    if overall_score >= proceed_threshold:
        return "Proceed"
    elif overall_score >= hold_threshold:
        return "Hold"
    else:
        return "Reject"


def save_rubric(name: str, yaml_text: str) -> dict:
    data = yaml.safe_load(yaml_text) or {}
    validate_rubric(data)
    path = rubric_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml_text, encoding="utf-8")
    return data
