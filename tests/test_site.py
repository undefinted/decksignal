import json

from helpers import product, write_json

from openpptbench.site import build_site


def test_build_site_creates_index_and_product_pages(tmp_path):
    rankings = {
        "schema_version": "0.2.0-draft",
        "leaderboards": {
            "overall": {
                "label_zh": "综合榜",
                "rows": [
                    {
                        "snapshot_id": "alpha__2026-09-01",
                        "product_id": "alpha",
                        "product": "Alpha",
                        "score": 82.0,
                        "eligible": True,
                        "coverage": 1.0,
                        "source_count": 2,
                        "rank": 1,
                        "capabilities": {"visual_design": 82.0},
                    }
                ],
            }
        },
    }
    ranking_path = write_json(tmp_path / "rankings.json", rankings)
    products_path = write_json(tmp_path / "products.json", product())

    result = build_site(ranking_path, products_path, tmp_path / "site")
    repeated = build_site(ranking_path, products_path, tmp_path / "site")

    assert result["pages"] == 3
    assert repeated["pages"] == 3
    assert "AI PPT 动态评测榜" in (tmp_path / "site" / "index.html").read_text(
        encoding="utf-8"
    )
    assert (tmp_path / "site" / "alpha.html").exists()
    assert (tmp_path / "site" / "methods.html").exists()
    parsed = json.loads((tmp_path / "site" / "rankings.json").read_text(encoding="utf-8"))
    assert parsed["leaderboards"]["overall"]["rows"][0]["rank"] == 1


def test_methods_page_contains_filters_and_workflow_details(tmp_path):
    rankings_path = write_json(
        tmp_path / "rankings.json", {"schema_version": "0.2.0-draft", "leaderboards": {}}
    )
    products_path = write_json(tmp_path / "products.json", product())
    workflows = tmp_path / "workflows"
    write_json(
        workflows / "method.json",
        {
            "schema_version": "0.3.0-draft",
            "snapshot_id": "method__2026-09-09",
            "workflow_id": "method",
            "name": "示例方法",
            "observed_at": "2026-09-09T00:00:00Z",
            "status": "documented",
            "source_refs": ["https://example.com/tutorial"],
            "steps": [{"order": 1, "action": "生成", "actor": "ai", "component": "Tool"}],
            "input_type": "提示词",
            "output_type": "pptx",
            "manual_effort_level": "low",
            "notes": "仅用于测试",
        },
    )

    result = build_site(
        rankings_path, products_path, tmp_path / "site", workflows_path=workflows
    )
    catalog = (tmp_path / "site" / "methods.html").read_text(encoding="utf-8")
    detail = (tmp_path / "site" / "method.html").read_text(encoding="utf-8")

    assert result["workflows"] == 1
    assert "全部状态" in catalog
    assert "示例方法" in catalog
    assert "https://example.com/tutorial" in detail
