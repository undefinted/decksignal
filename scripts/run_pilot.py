"""Validate and inspect local pilot submissions without inventing benchmark scores.

Expected layout::

    submissions/pilot/<product>/<task>/submission.json
    submissions/pilot/<product>/<task>/deck.pptx

The manifest is validated against the committed submission schema. Native PPTX
artifacts receive deterministic structural metrics; visual and external
benchmark scores remain explicitly pending until their adapters are run.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from openpptbench.inspect import inspect_pptx  # noqa: E402
from openpptbench.validate import load_data, validate_path  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="submissions/pilot")
    parser.add_argument("--output", default="results/raw/pilot")
    parser.add_argument("--schema", default="benchmark/schema/submission.schema.json")
    args = parser.parse_args()

    input_root = (ROOT / args.input).resolve()
    output_root = (ROOT / args.output).resolve()
    schema = (ROOT / args.schema).resolve()
    manifests = sorted(input_root.rglob("submission.json")) if input_root.exists() else []
    report: dict[str, object] = {
        "schema_version": "0.1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": str(input_root.relative_to(ROOT)),
        "manifest_count": len(manifests),
        "runs": [],
    }
    failures = 0
    for manifest_path in manifests:
        errors = validate_path(manifest_path, schema)
        manifest = load_data(manifest_path)
        artifact_path = manifest_path.parent / (manifest.get("artifact", {}).get("path") or "deck.pptx")
        run: dict[str, object] = {
            "manifest": str(manifest_path.relative_to(ROOT)),
            "submission_id": manifest.get("submission_id"),
            "product": manifest.get("product", {}).get("name"),
            "task_id": manifest.get("task_id"),
            "status": "ready" if not errors else "invalid_manifest",
            "validation_errors": errors,
            "artifact": str(artifact_path.relative_to(ROOT)) if artifact_path.exists() else None,
            "pending_layers": ["visual", "content", "editing", "operations"],
        }
        if errors:
            failures += 1
        elif not artifact_path.is_file():
            run["status"] = "missing_artifact"
            run["validation_errors"] = [{"message": "artifact file not found"}]
            failures += 1
        elif artifact_path.suffix.lower() == ".pptx":
            metrics = inspect_pptx(artifact_path)
            metrics_path = output_root / f"{manifest['submission_id']}.metrics.json"
            metrics_path.parent.mkdir(parents=True, exist_ok=True)
            metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            run["metrics"] = str(metrics_path.relative_to(ROOT))
            run["completed_layers"] = ["native_pptx_inspector"]
        else:
            run["status"] = "artifact_present_native_inspection_pending"
        report["runs"].append(run)  # type: ignore[union-attr]

    output_root.mkdir(parents=True, exist_ok=True)
    report_path = output_root / "pilot-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(report_path.relative_to(ROOT)), "runs": len(manifests), "failures": failures}, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
