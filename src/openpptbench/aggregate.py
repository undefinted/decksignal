from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

DIMENSION_WEIGHTS = {
    "content_quality": 0.25,
    "narrative_quality": 0.20,
    "visual_quality": 0.20,
    "instruction_following": 0.15,
    "editability": 0.10,
    "user_experience": 0.10,
}


def _load_submissions(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if source.is_dir():
        submissions = []
        for manifest in sorted(source.glob("*.json")):
            submissions.append(json.loads(manifest.read_text(encoding="utf-8")))
        return submissions
    data = json.loads(source.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else [data]


def _score(scores: dict[str, Any]) -> tuple[float, float]:
    missing = [dimension for dimension in DIMENSION_WEIGHTS if dimension not in scores]
    if missing:
        raise ValueError(f"Missing score dimensions: {', '.join(missing)}")
    numeric = {key: float(scores[key]) for key in DIMENSION_WEIGHTS}
    if any(value < 1 or value > 5 for value in numeric.values()):
        raise ValueError("Dimension scores must be between 1 and 5")
    weighted = sum(numeric[key] * weight for key, weight in DIMENSION_WEIGHTS.items())
    unweighted = sum(numeric.values()) / len(numeric)
    return round(weighted, 4), round(unweighted, 4)


def aggregate(path: str | Path) -> dict[str, Any]:
    submissions = _load_submissions(path)
    rows: list[dict[str, Any]] = []
    product_dimensions: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    for submission in submissions:
        scores = submission.get("scores") or {}
        weighted, unweighted = _score(scores)
        product = submission["product"]["name"]
        for dimension in DIMENSION_WEIGHTS:
            product_dimensions[product][dimension].append(float(scores[dimension]))
        rows.append(
            {
                "submission_id": submission["submission_id"],
                "task_id": submission["task_id"],
                "track": submission["track"],
                "product": product,
                "plan": submission["product"]["plan"],
                "weighted_score": weighted,
                "unweighted_score": unweighted,
                "dimensions": {key: float(scores[key]) for key in DIMENSION_WEIGHTS},
                "completed_at": submission["run"]["completed_at"],
            }
        )

    product_rows = []
    for product, dimensions in product_dimensions.items():
        means = {key: round(sum(values) / len(values), 4) for key, values in dimensions.items()}
        weighted, unweighted = _score(means)
        product_rows.append(
            {
                "product": product,
                "submission_count": len(next(iter(dimensions.values()))),
                "weighted_score": weighted,
                "unweighted_score": unweighted,
                "dimensions": means,
            }
        )
    product_rows.sort(key=lambda row: (-row["weighted_score"], row["product"].lower()))

    return {
        "schema_version": "0.1.0",
        "method": "mean expert scores with published v0.1 dimension weights",
        "weights": DIMENSION_WEIGHTS,
        "products": product_rows,
        "submissions": rows,
    }
