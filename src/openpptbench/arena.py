from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from .store import load_json_records

DIMENSIONS = ("content", "visual", "ready_to_use")


def aggregate_elo(
    reviews_path: str | Path,
    *,
    initial_rating: float = 1000.0,
    k_factor: float = 24.0,
) -> dict[str, Any]:
    reviews = sorted(load_json_records(reviews_path), key=lambda row: row["created_at"])
    ratings: dict[str, dict[str, float]] = defaultdict(
        lambda: {dimension: initial_rating for dimension in DIMENSIONS}
    )
    matches: dict[str, dict[str, int]] = defaultdict(
        lambda: {dimension: 0 for dimension in DIMENSIONS}
    )
    for review in reviews:
        left = review["left_submission_id"]
        right = review["right_submission_id"]
        if left == right:
            raise ValueError(f"Review compares a submission with itself: {review['review_id']}")
        for dimension in DIMENSIONS:
            choice = review["choices"][dimension]
            actual_left = 0.5 if choice == "tie" else (1.0 if choice == "left" else 0.0)
            expected_left = 1 / (1 + 10 ** ((ratings[right][dimension] - ratings[left][dimension]) / 400))
            delta = k_factor * (actual_left - expected_left)
            ratings[left][dimension] += delta
            ratings[right][dimension] -= delta
            matches[left][dimension] += 1
            matches[right][dimension] += 1

    rows = []
    for submission_id, dimension_ratings in ratings.items():
        mean_rating = sum(dimension_ratings.values()) / len(DIMENSIONS)
        rows.append(
            {
                "submission_id": submission_id,
                "rating": round(mean_rating, 2),
                "dimensions": {
                    key: round(value, 2) for key, value in dimension_ratings.items()
                },
                "matches": matches[submission_id],
                "provisional": min(matches[submission_id].values()) < 20,
            }
        )
    rows.sort(key=lambda row: (-row["rating"], row["submission_id"]))
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
    return {
        "schema_version": "0.2.0-draft",
        "method": "provisional sequential Elo; switch to Bradley-Terry for published batches",
        "review_count": len(reviews),
        "initial_rating": initial_rating,
        "k_factor": k_factor,
        "rows": rows,
    }

