import csv
import json

from openpptbench.adapters import (
    import_gloss_json,
    import_normalized_csv,
    import_presentbench_yaml,
    import_slidesgen_json,
    write_evidence_records,
)


def _registry(tmp_path):
    path = tmp_path / "registry.yaml"
    path.write_text(
        """sources:
  - {id: upstream, name: Upstream Bench, type: upstream_benchmark, url: https://example.com/bench}
  - {id: slidesgen-bench, name: SlidesGen-Bench, type: upstream_benchmark, url: https://example.com/slidesgen}
  - {id: presentbench, name: PresentBench, type: upstream_benchmark, url: https://example.com/presentbench}
  - {id: gloss, name: Gloss, type: upstream_benchmark, url: https://example.com/gloss}
""",
        encoding="utf-8",
    )
    return path


def test_csv_adapter_imports_normalized_evidence(tmp_path):
    registry = _registry(tmp_path)
    source = tmp_path / "input.csv"
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "product_snapshot_id",
                "capability",
                "raw_score",
                "raw_scale",
                "normalized_score",
                "sample_size",
                "observed_at",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "product_snapshot_id": "alpha__2026-09-01",
                "capability": "visual_design",
                "raw_score": "0.8",
                "raw_scale": "0-1",
                "normalized_score": "80",
                "sample_size": "10",
                "observed_at": "2026-09-01T00:00:00Z",
            }
        )

    records = import_normalized_csv(
        source,
        source_id="upstream",
        source_version="abc123",
        registry_path=registry,
    )
    written = write_evidence_records(records, tmp_path / "evidence")

    assert len(records) == 1
    assert records[0]["observation"]["normalized_score"] == 80
    assert records[0]["source"]["version"] == "abc123"
    assert len(written) == 1


def test_slidesgen_adapter_maps_content_and_visual_scores(tmp_path):
    source = tmp_path / "slidesgen.json"
    source.write_text(
        json.dumps(
            {
                "results": [
                    {
                        "content_score": 8,
                        "visual_design_score": 7,
                        "layout_score": 9,
                        "complexity_score": 8,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    records = import_slidesgen_json(
        source,
        product_snapshot_id="alpha__2026-09-01",
        source_version="commit",
        registry_path=_registry(tmp_path),
        observed_at="2026-09-01T00:00:00Z",
    )
    by_capability = {record["scope"]["capability"]: record for record in records}
    assert by_capability["content_grounding"]["observation"]["normalized_score"] == 80
    assert by_capability["visual_design"]["observation"]["normalized_score"] == 80


def test_presentbench_adapter_imports_only_grounded_section(tmp_path):
    source = tmp_path / "presentbench.yaml"
    source.write_text(
        """total:
  weighted_arithmetic_mean_percent: 80
  material_dependent:
    weighted_arithmetic_mean_percent: 75
    valid_count: 54
""",
        encoding="utf-8",
    )
    records = import_presentbench_yaml(
        source,
        product_snapshot_id="alpha__2026-09-01",
        source_version="commit",
        registry_path=_registry(tmp_path),
        observed_at="2026-09-01T00:00:00Z",
    )
    assert len(records) == 1
    assert records[0]["scope"]["capability"] == "content_grounding"
    assert records[0]["observation"]["sample_size"] == 54


def test_gloss_adapter_uses_verified_fidelity_score(tmp_path):
    source = tmp_path / "gloss.json"
    source.write_text(
        json.dumps(
            {
                "fidelity_score": 0.6768,
                "total_items": 280,
                "verification_complete": True,
                "verification_scope": "artifact_conformance",
                "eligible": False,
            }
        ),
        encoding="utf-8",
    )
    records = import_gloss_json(
        source,
        product_snapshot_id="alpha__2026-09-01",
        source_version="gloss-v1",
        registry_path=_registry(tmp_path),
        observed_at="2026-09-01T00:00:00Z",
    )
    assert records[0]["observation"]["normalized_score"] == 67.67999999999999
    assert records[0]["provenance"]["confidence_class"] == "A"
