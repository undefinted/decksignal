from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .store import index_by, latest_product_snapshots, load_json_records

CONFIDENCE_WEIGHTS = {"A": 1.0, "B": 0.7, "C": 0.4, "D": 0.0}
HALF_LIFE_DAYS = {
    "upstream_benchmark": 120,
    "local_run": 90,
    "blind_arena": 120,
    "expert_review": 120,
    "vendor_claim": 30,
    "community_report": 30,
}
REPRODUCIBLE_TYPES = {"upstream_benchmark", "local_run"}


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _freshness(observed_at: str, as_of: datetime, source_type: str) -> float:
    age = max(0.0, (as_of - _parse_datetime(observed_at)).total_seconds() / 86400)
    half_life = HALF_LIFE_DAYS.get(source_type, 90)
    return 2 ** (-age / half_life)


def _sample_quality(sample_size: int) -> float:
    # One observation remains useful, while 20+ observations receive full weight.
    return min(1.0, 0.25 + 0.75 * math.log2(max(1, sample_size) + 1) / math.log2(21))


def _matches_filters(evidence: dict[str, Any], filters: dict[str, Any]) -> bool:
    scope = evidence["scope"]
    return all(scope.get(key) == value for key, value in filters.items())


def _weighted_mean(items: list[tuple[float, float]]) -> float | None:
    denominator = sum(weight for _, weight in items)
    if not denominator:
        return None
    return sum(value * weight for value, weight in items) / denominator


def load_config(path: str | Path) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def build_rankings(
    evidence_path: str | Path,
    product_path: str | Path,
    config_path: str | Path,
    *,
    as_of: datetime | None = None,
) -> dict[str, Any]:
    evidence_records = load_json_records(evidence_path)
    product_records = load_json_records(product_path)
    products = index_by(product_records, "snapshot_id")
    current_snapshot_ids = {
        record["snapshot_id"] for record in latest_product_snapshots(product_records).values()
    }
    config = load_config(config_path)
    as_of = as_of or datetime.now(timezone.utc)
    if as_of.tzinfo is None:
        as_of = as_of.replace(tzinfo=timezone.utc)

    results: dict[str, Any] = {}
    for board_id, board in config["leaderboards"].items():
        required = board["capabilities"]
        filters = board.get("filters", {})
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for evidence in evidence_records:
            if evidence["product_snapshot_id"] not in current_snapshot_ids:
                continue
            if evidence["scope"]["capability"] not in required:
                continue
            if not _matches_filters(evidence, filters):
                continue
            if evidence["product_snapshot_id"] not in products:
                raise ValueError(
                    f"Unknown product snapshot: {evidence['product_snapshot_id']}"
                )
            grouped[evidence["product_snapshot_id"]].append(evidence)

        rows = []
        for snapshot_id, records in grouped.items():
            by_capability: dict[str, list[tuple[float, float]]] = defaultdict(list)
            source_names: set[str] = set()
            reproducible = False
            newest: datetime | None = None
            total_effective_weight = 0.0
            for evidence in records:
                normalized = evidence["observation"].get("normalized_score")
                if normalized is None:
                    continue
                source_type = evidence["source"]["type"]
                confidence = CONFIDENCE_WEIGHTS[evidence["provenance"]["confidence_class"]]
                freshness = _freshness(
                    evidence["provenance"]["observed_at"], as_of, source_type
                )
                quality = _sample_quality(evidence["observation"]["sample_size"])
                effective_weight = confidence * freshness * quality
                if not effective_weight:
                    continue
                capability = evidence["scope"]["capability"]
                by_capability[capability].append((float(normalized), effective_weight))
                total_effective_weight += effective_weight
                source_names.add(evidence["source"]["name"])
                reproducible = reproducible or source_type in REPRODUCIBLE_TYPES
                observed = _parse_datetime(evidence["provenance"]["observed_at"])
                newest = observed if newest is None or observed > newest else newest

            capability_scores = {
                capability: round(score, 3)
                for capability, observations in by_capability.items()
                if (score := _weighted_mean(observations)) is not None
            }
            coverage = len(capability_scores) / len(required) if required else 0.0
            capability_config = config["capabilities"]
            score_items = [
                (capability_scores[key], float(capability_config[key]["weight"]))
                for key in required
                if key in capability_scores
            ]
            score = _weighted_mean(score_items)
            eligible = (
                coverage >= float(board["minimum_coverage"])
                and len(source_names) >= int(board["minimum_sources"])
                and (not board.get("require_reproducible") or reproducible)
            )
            product = products[snapshot_id]
            rows.append(
                {
                    "snapshot_id": snapshot_id,
                    "product_id": product["product_id"],
                    "product": product["name"],
                    "score": round(score, 3) if score is not None else None,
                    "eligible": eligible,
                    "coverage": round(coverage, 4),
                    "source_count": len(source_names),
                    "evidence_count": len(records),
                    "effective_evidence_weight": round(total_effective_weight, 4),
                    "newest_evidence_at": newest.isoformat() if newest else None,
                    "capabilities": capability_scores,
                    "missing_capabilities": [
                        capability for capability in required if capability not in capability_scores
                    ],
                }
            )
        rows.sort(
            key=lambda row: (
                not row["eligible"],
                -(row["score"] if row["score"] is not None else -1),
                row["product"].lower(),
            )
        )
        for rank, row in enumerate((row for row in rows if row["eligible"]), start=1):
            row["rank"] = rank
        for row in rows:
            row.setdefault("rank", None)
        results[board_id] = {
            "label_zh": board["label_zh"],
            "requirements": {
                "capabilities": required,
                "minimum_coverage": board["minimum_coverage"],
                "minimum_sources": board["minimum_sources"],
                "require_reproducible": board.get("require_reproducible", False),
                "filters": filters,
            },
            "rows": rows,
        }

    return {
        "schema_version": "0.2.0-draft",
        "generated_at": as_of.isoformat(),
        "method": "source-normalized, confidence-, freshness-, and coverage-aware aggregation",
        "leaderboards": results,
    }
