import json
from pathlib import Path


def write_json(path: Path, data: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def product(snapshot_id: str = "alpha__2026-09-01", name: str = "Alpha") -> dict:
    return {
        "schema_version": "0.2.0-draft",
        "snapshot_id": snapshot_id,
        "product_id": name.lower(),
        "name": name,
        "provider": name,
        "kind": "end_user_product",
        "canonical_url": "https://example.com/",
        "observed_at": "2026-09-01T00:00:00Z",
        "status": "evaluated",
        "facts": {},
    }


def evidence(
    capability: str,
    score: float,
    *,
    evidence_id: str,
    snapshot_id: str = "alpha__2026-09-01",
    source_name: str = "Local",
    source_type: str = "local_run",
    observed_at: str = "2026-09-01T00:00:00Z",
    scenario: str = "business",
    language: str = "zh-CN",
) -> dict:
    return {
        "schema_version": "0.2.0-draft",
        "evidence_id": evidence_id,
        "product_snapshot_id": snapshot_id,
        "source": {
            "name": source_name,
            "type": source_type,
            "version": "test",
            "url": None,
            "adapter_version": None,
        },
        "scope": {
            "track": "prompt_to_deck",
            "scenario": scenario,
            "language": language,
            "capability": capability,
            "task_ids": ["task-1"],
        },
        "observation": {
            "raw_score": score,
            "raw_scale": "0-100",
            "normalized_score": score,
            "sample_size": 10,
            "uncertainty": None,
        },
        "provenance": {
            "observed_at": observed_at,
            "recorded_at": observed_at,
            "confidence_class": "A",
            "artifacts_available": True,
            "artifact_refs": [],
            "notes": "test",
        },
    }

