from datetime import datetime, timezone

from helpers import evidence, product, write_json

from openpptbench.ranking import build_rankings


def _config(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text(
        """capabilities:
  content_grounding: {weight: 0.6}
  visual_design: {weight: 0.4}
leaderboards:
  overall:
    label_zh: 综合榜
    capabilities: [content_grounding, visual_design]
    minimum_coverage: 1.0
    minimum_sources: 2
    require_reproducible: true
""",
        encoding="utf-8",
    )
    return path


def test_ranking_requires_coverage_and_multiple_sources(tmp_path):
    products = write_json(tmp_path / "products.json", product())
    records = [
        evidence("content_grounding", 90, evidence_id="a", source_name="Local"),
        evidence(
            "visual_design",
            70,
            evidence_id="b",
            source_name="Upstream",
            source_type="upstream_benchmark",
        ),
    ]
    evidence_path = write_json(tmp_path / "evidence.json", records)

    result = build_rankings(
        evidence_path,
        products,
        _config(tmp_path),
        as_of=datetime(2026, 9, 6, tzinfo=timezone.utc),
    )
    row = result["leaderboards"]["overall"]["rows"][0]

    assert row["eligible"] is True
    assert row["rank"] == 1
    assert row["coverage"] == 1
    assert row["score"] == 82


def test_ranking_marks_partial_product_ineligible(tmp_path):
    products = write_json(tmp_path / "products.json", product())
    evidence_path = write_json(
        tmp_path / "evidence.json",
        evidence("content_grounding", 95, evidence_id="partial"),
    )

    result = build_rankings(
        evidence_path,
        products,
        _config(tmp_path),
        as_of=datetime(2026, 9, 6, tzinfo=timezone.utc),
    )
    row = result["leaderboards"]["overall"]["rows"][0]

    assert row["eligible"] is False
    assert row["rank"] is None
    assert row["coverage"] == 0.5
    assert row["missing_capabilities"] == ["visual_design"]


def test_fresh_evidence_outweighs_old_evidence(tmp_path):
    products = write_json(tmp_path / "products.json", product())
    records = [
        evidence(
            "content_grounding",
            20,
            evidence_id="old",
            observed_at="2025-09-01T00:00:00Z",
        ),
        evidence(
            "content_grounding",
            80,
            evidence_id="new",
            observed_at="2026-09-01T00:00:00Z",
        ),
    ]
    evidence_path = write_json(tmp_path / "evidence.json", records)
    result = build_rankings(
        evidence_path,
        products,
        _config(tmp_path),
        as_of=datetime(2026, 9, 6, tzinfo=timezone.utc),
    )
    score = result["leaderboards"]["overall"]["rows"][0]["capabilities"][
        "content_grounding"
    ]
    assert score > 70


def test_current_board_excludes_historical_product_snapshot(tmp_path):
    older = product("alpha__2026-08-01", "Alpha")
    older["observed_at"] = "2026-08-01T00:00:00Z"
    newer = product("alpha__2026-09-01", "Alpha")
    products = write_json(tmp_path / "products.json", [older, newer])
    records = [
        evidence(
            "content_grounding",
            99,
            evidence_id="old",
            snapshot_id="alpha__2026-08-01",
        ),
        evidence("content_grounding", 60, evidence_id="new"),
    ]
    evidence_path = write_json(tmp_path / "evidence.json", records)

    result = build_rankings(
        evidence_path,
        products,
        _config(tmp_path),
        as_of=datetime(2026, 9, 6, tzinfo=timezone.utc),
    )
    rows = result["leaderboards"]["overall"]["rows"]

    assert len(rows) == 1
    assert rows[0]["snapshot_id"] == "alpha__2026-09-01"


def test_workflow_can_be_ranked_as_a_distinct_subject(tmp_path):
    products_dir = tmp_path / "products"
    products_dir.mkdir()
    workflow = {
        "schema_version": "0.3.0-draft",
        "snapshot_id": "outline-image-layout__2026-09-01",
        "workflow_id": "outline-image-layout",
        "name": "大纲＋配图＋排版工作流",
        "observed_at": "2026-09-01T00:00:00Z",
        "status": "evaluated",
        "source_refs": ["https://example.com/method"],
        "steps": [{"order": 1, "action": "生成大纲", "actor": "ai"}],
        "output_type": "pptx",
    }
    workflows = write_json(tmp_path / "workflows.json", workflow)
    record = evidence(
        "content_grounding",
        88,
        evidence_id="workflow-score",
        snapshot_id="unused",
    )
    record.pop("product_snapshot_id")
    record["subject"] = {
        "kind": "workflow",
        "snapshot_id": "outline-image-layout__2026-09-01",
    }
    evidence_path = write_json(tmp_path / "evidence.json", record)

    result = build_rankings(
        evidence_path,
        products_dir,
        _config(tmp_path),
        workflow_path=workflows,
        as_of=datetime(2026, 9, 6, tzinfo=timezone.utc),
    )
    row = result["leaderboards"]["overall"]["rows"][0]

    assert row["subject_kind"] == "workflow"
    assert row["subject_id"] == "outline-image-layout"
