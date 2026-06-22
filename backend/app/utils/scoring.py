from typing import Any


def weighted_score(sub_scores: dict[str, float], weights: dict[str, float] | None = None) -> float:
    """Aggregate sub-scores (0-100) into an overall score."""
    if not sub_scores:
        return 0.0
    if weights is None:
        weights = {k: 1.0 for k in sub_scores}
    total_weight = sum(weights.get(k, 1.0) for k in sub_scores)
    if total_weight == 0:
        return 0.0
    score = sum(sub_scores[k] * weights.get(k, 1.0) for k in sub_scores) / total_weight
    return round(max(0.0, min(100.0, score)), 2)


def normalize_pct_to_score(pct: float, invert: bool = False) -> float:
    """Convert a 0-100 percentage to a score. If invert=True, lower pct is better."""
    val = 100.0 - pct if invert else pct
    return round(max(0.0, min(100.0, val)), 2)


def score_from_ratio(good: float, total: float) -> float:
    if total <= 0:
        return 100.0
    return round(max(0.0, min(100.0, (good / total) * 100)), 2)
