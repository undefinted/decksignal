from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def load_json_records(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(source)
    if source.is_dir():
        records: list[dict[str, Any]] = []
        for item in sorted(source.rglob("*.json")):
            data = json.loads(item.read_text(encoding="utf-8"))
            records.extend(data if isinstance(data, list) else [data])
        return records
    data = json.loads(source.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else [data]


def write_json(data: Any, path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def index_by(records: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        value = str(record[key])
        if value in indexed:
            raise ValueError(f"Duplicate {key}: {value}")
        indexed[value] = record
    return indexed


def latest_product_snapshots(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for record in records:
        product_id = record["product_id"]
        current = latest.get(product_id)
        if current is None or datetime.fromisoformat(
            record["observed_at"].replace("Z", "+00:00")
        ) > datetime.fromisoformat(current["observed_at"].replace("Z", "+00:00")):
            latest[product_id] = record
    return latest
