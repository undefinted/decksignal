from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .store import load_json_records


def _check_one(product: dict[str, Any], timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(
        product["canonical_url"],
        headers={"User-Agent": "DeckSignal-Monitor/0.2 (+https://github.com/)"},
        method="HEAD",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status_code = response.status
            final_url = response.url
            error = None
    except urllib.error.HTTPError as exc:
        status_code = exc.code
        final_url = exc.url
        error = str(exc)
    except (urllib.error.URLError, TimeoutError) as exc:
        status_code = None
        final_url = None
        error = str(exc)
    return {
        "snapshot_id": product["snapshot_id"],
        "product_id": product["product_id"],
        "url": product["canonical_url"],
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status_code": status_code,
        "final_url": final_url,
        "reachable": status_code is not None and status_code < 500,
        "error": error,
    }


def check_products(product_path: str | Path, *, timeout: float = 10, workers: int = 6) -> dict[str, Any]:
    products = load_json_records(product_path)
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        checks = list(executor.map(lambda product: _check_one(product, timeout), products))
    return {
        "schema_version": "0.2.0-draft",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
    }


def merge_discoveries(input_path: str | Path, queue_path: str | Path) -> dict[str, Any]:
    incoming = load_json_records(input_path)
    destination = Path(queue_path)
    existing = load_json_records(destination) if destination.exists() else []
    by_id = {record["candidate_id"]: record for record in existing}
    added = 0
    for record in incoming:
        if record["candidate_id"] not in by_id:
            by_id[record["candidate_id"]] = record
            added += 1
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(list(by_id.values()), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"added": added, "total": len(by_id), "queue": str(destination)}


def discover_github(
    queries: list[str], *, per_query: int = 10, token: str | None = None
) -> list[dict[str, Any]]:
    token = token or os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "DeckSignal-Discovery/0.2",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    discovered: dict[str, dict[str, Any]] = {}
    now = datetime.now(timezone.utc).isoformat()
    for query in queries:
        encoded = urllib.parse.urlencode(
            {"q": query, "sort": "updated", "order": "desc", "per_page": per_query}
        )
        request = urllib.request.Request(
            f"https://api.github.com/search/repositories?{encoded}", headers=headers
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        for item in payload.get("items", []):
            full_name = item["full_name"]
            candidate_id = "github-" + full_name.lower().replace("/", "--")
            discovered[candidate_id] = {
                "schema_version": "0.2.0-draft",
                "candidate_id": candidate_id,
                "name": full_name,
                "url": item["html_url"],
                "discovered_at": now,
                "source_type": "repository",
                "source_url": item["html_url"],
                "status": "new",
                "notes": f"GitHub query: {query}; description: {item.get('description') or ''}",
            }
    return sorted(discovered.values(), key=lambda record: record["candidate_id"])
