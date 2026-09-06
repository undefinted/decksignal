from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from .store import latest_product_snapshots, load_json_records

STYLE = """
:root{font-family:Inter,ui-sans-serif,system-ui,sans-serif;color:#172033;background:#f6f7fb}
*{box-sizing:border-box}body{margin:0}.wrap{max-width:1120px;margin:auto;padding:32px 20px 64px}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:28px}a{color:#4057c9}
.brand{font-weight:800;font-size:20px;color:#172033;text-decoration:none}.muted{color:#667085}
.hero{background:linear-gradient(135deg,#172033,#4057c9);color:white;padding:32px;border-radius:20px;margin-bottom:24px}
.hero h1{margin:0 0 8px;font-size:36px}.tabs{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}
.tabs a,.pill{background:white;border:1px solid #dde1ef;border-radius:999px;padding:8px 12px;text-decoration:none}
.card{background:white;border:1px solid #e6e8f0;border-radius:16px;padding:20px;margin:14px 0;box-shadow:0 5px 18px #1720330a}
table{border-collapse:collapse;width:100%;background:white;border-radius:14px;overflow:hidden}th,td{padding:13px;text-align:left;border-bottom:1px solid #eef0f5}th{background:#f0f2f8}
.score{font-weight:800;font-size:18px}.ok{color:#14804a}.wait{color:#9a6700}.bar{height:8px;background:#ebedf5;border-radius:99px;overflow:hidden}.bar span{display:block;height:100%;background:#596dde}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}.metric{padding:14px;background:#f8f9fc;border-radius:12px}
footer{margin-top:42px;color:#667085;font-size:13px}@media(max-width:700px){.hero h1{font-size:28px}table{font-size:13px}.hide-sm{display:none}}
"""


def _page(title: str, body: str) -> str:
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><link rel="stylesheet" href="assets/style.css"></head><body><div class="wrap"><header><a class="brand" href="index.html">OpenPPTBench</a><span class="muted">开放、可追溯、持续更新</span></header>{body}<footer>所有分数均应链接到证据。未达到覆盖门槛的产品不参与正式排名。</footer></div></body></html>"""


def _board_table(board: dict[str, Any]) -> str:
    rows = []
    for row in board["rows"]:
        status = '<span class="ok">正式</span>' if row["eligible"] else '<span class="wait">证据不足</span>'
        score = f"{row['score']:.1f}" if row["score"] is not None else "—"
        rank = str(row["rank"]) if row["rank"] else "—"
        rows.append(
            f"<tr><td>{rank}</td><td><a href=\"{html.escape(row['product_id'])}.html\">{html.escape(row['product'])}</a></td><td class=\"score\">{score}</td><td>{row['coverage']*100:.0f}%</td><td class=\"hide-sm\">{row['source_count']}</td><td>{status}</td></tr>"
        )
    if not rows:
        return '<div class="card"><p>尚无符合该榜单范围的证据。</p></div>'
    return "<table><thead><tr><th>#</th><th>产品</th><th>分数</th><th>覆盖度</th><th class=\"hide-sm\">来源</th><th>状态</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"


def _product_page(product: dict[str, Any], boards: dict[str, Any]) -> str:
    appearances = []
    for board in boards.values():
        for row in board["rows"]:
            if row["snapshot_id"] != product["snapshot_id"]:
                continue
            capabilities = "".join(
                f'<div class="metric"><strong>{html.escape(name)}</strong><div class="score">{value:.1f}</div><div class="bar"><span style="width:{max(0,min(100,value))}%"></span></div></div>'
                for name, value in row["capabilities"].items()
            )
            appearances.append(
                f'<section class="card"><h2>{html.escape(board["label_zh"])}</h2><p>分数：<strong>{row["score"] if row["score"] is not None else "—"}</strong> · 覆盖度：{row["coverage"]*100:.0f}% · 证据来源：{row["source_count"]}</p><div class="grid">{capabilities}</div></section>'
            )
    body = f'<div class="hero"><h1>{html.escape(product["name"])}</h1><p>状态：{html.escape(product["status"])} · 快照：{html.escape(product["snapshot_id"])}</p><a class="pill" href="{html.escape(product["canonical_url"])}">产品官网</a></div>'
    body += "".join(appearances) or '<div class="card"><p>该产品尚无评测证据。</p></div>'
    return _page(product["name"], body)


def build_site(rankings_path: str | Path, products_path: str | Path, output_dir: str | Path) -> dict[str, Any]:
    rankings = json.loads(Path(rankings_path).read_text(encoding="utf-8"))
    product_records = load_json_records(products_path)
    products = latest_product_snapshots(product_records)
    output = Path(output_dir)
    (output / "assets").mkdir(parents=True, exist_ok=True)
    (output / "assets" / "style.css").write_text(STYLE.strip() + "\n", encoding="utf-8")
    (output / "rankings.json").write_text(json.dumps(rankings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    boards = rankings["leaderboards"]
    tabs = "".join(f'<a href="#{html.escape(key)}">{html.escape(board["label_zh"])}</a>' for key, board in boards.items())
    sections = "".join(f'<section id="{html.escape(key)}"><h2>{html.escape(board["label_zh"])}</h2>{_board_table(board)}</section>' for key, board in boards.items())
    body = f'<div class="hero"><h1>AI PPT 动态评测榜</h1><p>聚合独立 benchmark、本地可复现评测和盲评证据；同时呈现分数、覆盖度与证据状态。</p></div><nav class="tabs">{tabs}</nav>{sections}'
    (output / "index.html").write_text(_page("AI PPT 动态评测榜", body), encoding="utf-8")

    product_ids_written: set[str] = set()
    for snapshot in products.values():
        (output / f"{snapshot['product_id']}.html").write_text(_product_page(snapshot, boards), encoding="utf-8")
        product_ids_written.add(snapshot["product_id"])
    return {"output": str(output), "pages": 1 + len(product_ids_written), "products": len(product_ids_written), "leaderboards": len(boards)}
