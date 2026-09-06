from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REQUIRED_COLUMNS = {
    "product_snapshot_id",
    "capability",
    "raw_score",
    "raw_scale",
    "normalized_score",
    "sample_size",
    "observed_at",
}


def _load_source(source_id: str, registry_path: str | Path) -> dict[str, Any]:
    registry = yaml.safe_load(Path(registry_path).read_text(encoding="utf-8"))
    for source in registry["sources"]:
        if source["id"] == source_id:
            return source
    raise ValueError(f"Unknown source id: {source_id}")


def import_normalized_csv(
    input_path: str | Path,
    *,
    source_id: str,
    source_version: str,
    registry_path: str | Path,
    adapter_version: str = "0.1.0",
) -> list[dict[str, Any]]:
    source = _load_source(source_id, registry_path)
    records: list[dict[str, Any]] = []
    with Path(input_path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing adapter columns: {', '.join(sorted(missing))}")
        for row_number, row in enumerate(reader, start=2):
            normalized = float(row["normalized_score"])
            if not 0 <= normalized <= 100:
                raise ValueError(f"Row {row_number}: normalized_score must be in [0, 100]")
            observed_at = row["observed_at"]
            evidence_id = row.get("evidence_id") or (
                f"{source_id}__{row['product_snapshot_id']}__{row['capability']}__{row_number}"
            )
            record = {
                "schema_version": "0.2.0-draft",
                "evidence_id": evidence_id,
                "product_snapshot_id": row["product_snapshot_id"],
                "source": {
                    "name": source["name"],
                    "type": source["type"],
                    "version": source_version,
                    "url": source.get("url"),
                    "adapter_version": adapter_version,
                },
                "scope": {
                    "track": row.get("track") or "prompt_to_deck",
                    "scenario": row.get("scenario") or "general",
                    "language": row.get("language") or "und",
                    "capability": row["capability"],
                    "task_ids": [item for item in (row.get("task_ids") or "").split("|") if item],
                },
                "observation": {
                    "raw_score": float(row["raw_score"]),
                    "raw_scale": row["raw_scale"],
                    "normalized_score": normalized,
                    "sample_size": int(row["sample_size"]),
                    "uncertainty": float(row["uncertainty"])
                    if row.get("uncertainty")
                    else None,
                },
                "provenance": {
                    "observed_at": observed_at,
                    "recorded_at": datetime.now(timezone.utc).isoformat(),
                    "confidence_class": row.get("confidence_class") or "B",
                    "artifacts_available": (row.get("artifacts_available") or "false").lower()
                    == "true",
                    "artifact_refs": [
                        item for item in (row.get("artifact_refs") or "").split("|") if item
                    ],
                    "notes": row.get("notes") or "",
                },
            }
            records.append(record)
    return records


def write_evidence_records(records: list[dict[str, Any]], output_dir: str | Path) -> list[str]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for record in records:
        path = destination / f"{record['evidence_id']}.json"
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        written.append(str(path))
    return written


def _evidence_record(
    *,
    evidence_id: str,
    product_snapshot_id: str,
    source: dict[str, Any],
    source_version: str,
    adapter_version: str,
    capability: str,
    raw_score: float,
    raw_scale: str,
    normalized_score: float,
    sample_size: int,
    observed_at: str,
    track: str,
    scenario: str,
    language: str,
    notes: str,
    artifacts_available: bool = True,
) -> dict[str, Any]:
    return {
        "schema_version": "0.2.0-draft",
        "evidence_id": evidence_id,
        "product_snapshot_id": product_snapshot_id,
        "source": {
            "name": source["name"],
            "type": source["type"],
            "version": source_version,
            "url": source.get("url"),
            "adapter_version": adapter_version,
        },
        "scope": {
            "track": track,
            "scenario": scenario,
            "language": language,
            "capability": capability,
            "task_ids": [],
        },
        "observation": {
            "raw_score": raw_score,
            "raw_scale": raw_scale,
            "normalized_score": max(0.0, min(100.0, normalized_score)),
            "sample_size": sample_size,
            "uncertainty": None,
        },
        "provenance": {
            "observed_at": observed_at,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "confidence_class": "A",
            "artifacts_available": artifacts_available,
            "artifact_refs": [],
            "notes": notes,
        },
    }


def import_slidesgen_json(
    input_path: str | Path,
    *,
    product_snapshot_id: str,
    source_version: str,
    registry_path: str | Path,
    observed_at: str,
    scenario: str = "general",
    language: str = "und",
) -> list[dict[str, Any]]:
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    results = payload.get("results") or []
    if not results:
        raise ValueError("SlidesGen-Bench output has no results")
    source = _load_source("slidesgen-bench", registry_path)
    values: dict[str, list[float]] = defaultdict(list)
    for result in results:
        if result.get("content_score") is not None:
            values["content_grounding"].append(float(result["content_score"]))
        visual_parts = [
            float(result[key])
            for key in ("visual_design_score", "layout_score", "complexity_score")
            if result.get(key) is not None
        ]
        if visual_parts:
            values["visual_design"].append(sum(visual_parts) / len(visual_parts))
    records = []
    for capability, scores in values.items():
        mean = sum(scores) / len(scores)
        records.append(
            _evidence_record(
                evidence_id=f"slidesgen-bench__{product_snapshot_id}__{capability}",
                product_snapshot_id=product_snapshot_id,
                source=source,
                source_version=source_version,
                adapter_version="slidesgen-0.1.0",
                capability=capability,
                raw_score=mean,
                raw_scale="1-10 upstream criterion score",
                normalized_score=mean * 10,
                sample_size=len(scores),
                observed_at=observed_at,
                track="prompt_to_deck",
                scenario=scenario,
                language=language,
                notes=(
                    "Content maps directly from content_score. Visual design is the mean of "
                    "visual_design_score, layout_score, and complexity_score."
                ),
            )
        )
    return records


def import_presentbench_yaml(
    input_path: str | Path,
    *,
    product_snapshot_id: str,
    source_version: str,
    registry_path: str | Path,
    observed_at: str,
    scenario: str = "general",
    language: str = "und",
) -> list[dict[str, Any]]:
    payload = yaml.safe_load(Path(input_path).read_text(encoding="utf-8"))
    total = payload.get("total") or {}
    dependent = total.get("material_dependent") or {}
    score = dependent.get("weighted_arithmetic_mean_percent")
    if score is None:
        raise ValueError("PresentBench score YAML lacks material_dependent score")
    sample_size = int(dependent.get("valid_count") or 1)
    source = _load_source("presentbench", registry_path)
    return [
        _evidence_record(
            evidence_id=f"presentbench__{product_snapshot_id}__content-grounding",
            product_snapshot_id=product_snapshot_id,
            source=source,
            source_version=source_version,
            adapter_version="presentbench-0.1.0",
            capability="content_grounding",
            raw_score=float(score),
            raw_scale="0-100 material-dependent checklist score",
            normalized_score=float(score),
            sample_size=sample_size,
            observed_at=observed_at,
            track="document_to_deck",
            scenario=scenario,
            language=language,
            notes=(
                "Only PresentBench material-dependent checklist results map to content_grounding; "
                "the overall and material-independent composites remain upstream-only metrics."
            ),
        )
    ]


def import_gloss_json(
    input_path: str | Path,
    *,
    product_snapshot_id: str,
    source_version: str,
    registry_path: str | Path,
    observed_at: str,
    scenario: str = "artifact_conformance",
    language: str = "und",
) -> list[dict[str, Any]]:
    payload = json.loads(Path(input_path).read_text(encoding="utf-8"))
    score = payload.get("fidelity_score")
    if score is None:
        raise ValueError("Gloss report lacks fidelity_score")
    total_items = int(payload.get("total_items") or 1)
    source = _load_source("gloss", registry_path)
    confidence = "A" if payload.get("verification_complete") else "C"
    record = _evidence_record(
        evidence_id=f"gloss__{product_snapshot_id}__native-editability",
        product_snapshot_id=product_snapshot_id,
        source=source,
        source_version=source_version,
        adapter_version="gloss-0.1.0",
        capability="native_editability",
        raw_score=float(score),
        raw_scale="0-1 Gloss fidelity_score",
        normalized_score=float(score) * 100,
        sample_size=total_items,
        observed_at=observed_at,
        track="artifact_conformance",
        scenario=scenario,
        language=language,
        notes=(
            f"Gloss verification scope: {payload.get('verification_scope', 'unknown')}; "
            f"eligibility: {payload.get('eligible')}."
        ),
    )
    record["provenance"]["confidence_class"] = confidence
    return [record]


UPSTREAM_IMPORTERS = {
    "slidesgen": import_slidesgen_json,
    "presentbench": import_presentbench_yaml,
    "gloss": import_gloss_json,
}


def import_upstream(name: str, input_path: str | Path, **kwargs: Any) -> list[dict[str, Any]]:
    try:
        importer = UPSTREAM_IMPORTERS[name]
    except KeyError as exc:
        raise ValueError(f"Unknown adapter: {name}") from exc
    return importer(input_path, **kwargs)
