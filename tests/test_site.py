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

    assert result["pages"] == 2
    assert repeated["pages"] == 2
    assert "AI PPT 动态评测榜" in (tmp_path / "site" / "index.html").read_text(
        encoding="utf-8"
    )
    assert (tmp_path / "site" / "alpha.html").exists()
    parsed = json.loads((tmp_path / "site" / "rankings.json").read_text(encoding="utf-8"))
    assert parsed["leaderboards"]["overall"]["rows"][0]["rank"] == 1
