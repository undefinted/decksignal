from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import yaml

from .store import latest_product_snapshots, latest_snapshots, load_json_records

STYLE = """
:root{font-family:Inter,ui-sans-serif,system-ui,sans-serif;color:#172033;background:#f6f7fb}
*{box-sizing:border-box}body{margin:0}.wrap{max-width:1120px;margin:auto;padding:32px 20px 64px}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:28px;gap:16px}a{color:#4057c9}
.brand{font-weight:800;font-size:20px;color:#172033;text-decoration:none}.muted{color:#667085}
.topnav{display:flex;gap:14px;align-items:center}.topnav a{text-decoration:none;font-weight:650}
.hero{background:linear-gradient(135deg,#172033,#4057c9);color:white;padding:32px;border-radius:20px;margin-bottom:24px}
.hero h1{margin:0 0 8px;font-size:36px}.tabs{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}
.tabs a,.pill{background:white;border:1px solid #dde1ef;border-radius:999px;padding:8px 12px;text-decoration:none}
.card{background:white;border:1px solid #e6e8f0;border-radius:16px;padding:20px;margin:14px 0;box-shadow:0 5px 18px #1720330a}
table{border-collapse:collapse;width:100%;background:white;border-radius:14px;overflow:hidden}th,td{padding:13px;text-align:left;border-bottom:1px solid #eef0f5}th{background:#f0f2f8}
.score{font-weight:800;font-size:18px}.ok{color:#14804a}.wait{color:#9a6700}.bar{height:8px;background:#ebedf5;border-radius:99px;overflow:hidden}.bar span{display:block;height:100%;background:#596dde}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}.metric{padding:14px;background:#f8f9fc;border-radius:12px}.kpi{font-size:30px;font-weight:850;display:block}.notice{border-left:4px solid #d99a18;background:#fff9e8}.empty{padding:18px;background:#f8f9fc;border-radius:12px;color:#667085}
.filters{display:flex;gap:10px;flex-wrap:wrap}.filters input,.filters select{padding:10px 12px;border:1px solid #d8ddea;border-radius:10px;background:white;font:inherit}.method h2{margin:0 0 6px}.method-meta{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.tag{font-size:12px;background:#eef1ff;color:#3347a5;border-radius:999px;padding:5px 8px}.sources li{margin:7px 0}.steps li{margin:10px 0}
footer{margin-top:42px;color:#667085;font-size:13px}@media(max-width:700px){.hero h1{font-size:28px}table{font-size:13px}.hide-sm{display:none}}
"""


def _page(title: str, body: str) -> str:
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} · DeckSignal</title><link rel="stylesheet" href="assets/style.css"></head><body><div class="wrap"><header><a class="brand" href="index.html">DeckSignal</a><nav class="topnav"><a href="benchmarks.html">Benchmark</a><a href="research.html">工具全景</a><a href="methods.html">方法库</a><span class="muted">AI 演示智鉴</span></nav></header>{body}<footer>所有分数均应链接到证据。发现与整理不等于实测；未达到覆盖门槛的对象不参与正式排名。评测由 OpenPPTBench 引擎驱动。</footer></div></body></html>"""


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


def _source_block(ref: str, sources: dict[str, dict[str, Any]]) -> str:
    source = sources.get(ref) or next((item for item in sources.values() if item["url"] == ref), None)
    if source is None:
        return f'<li><a href="{html.escape(ref)}">{html.escape(ref)}</a> <span class="wait">（元数据待补）</span></li>' if ref.startswith("http") else f'<li>{html.escape(ref)} <span class="wait">（元数据待补）</span></li>'
    author = source.get("author") or "作者待核实"
    published = source.get("published_at") or "发布日期待核实"
    supports = "；".join(source.get("supports", []))
    return f'<li><a href="{html.escape(source["url"])}"><strong>{html.escape(source["title"])}</strong></a><br><span class="muted">{html.escape(source["platform"])} · {html.escape(author)} · {html.escape(published)} · 收录 {html.escape(source["accessed_at"])} · {html.escape(source.get("evidence_nature", "未分类"))} · {html.escape(source["rights"])}</span><br>支持内容：{html.escape(supports)}</li>'


def _product_page(product: dict[str, Any], boards: dict[str, Any], sources: dict[str, dict[str, Any]]) -> str:
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
    source_url = product.get("canonical_url") or product.get("source_refs", ["#"])[0]
    kind_label = "工具" if product.get("subject_kind") == "product" else "方法工作流"
    body = f'<div class="hero"><h1>{html.escape(product["name"])}</h1><p>类型：{kind_label} · 状态：{html.escape(product["status"])} · 快照：{html.escape(product["snapshot_id"])}</p><a class="pill" href="{html.escape(source_url)}">查看来源</a></div>'
    if product.get("subject_kind") == "workflow":
        steps = "".join(
            f'<li><strong>{step["order"]}.</strong> {html.escape(step["action"])} <span class="muted">（{html.escape(step["actor"])} · {html.escape(step.get("component") or "未注明")}）</span></li>'
            for step in product.get("steps", [])
        )
        source_items = "".join(
            _source_block(ref, sources)
            for ref in product.get("source_refs", [])
        )
        body += f'<section class="card"><h2>方法步骤</h2><ol class="steps">{steps}</ol><p><strong>输入：</strong>{html.escape(product.get("input_type", "未注明"))} · <strong>输出：</strong>{html.escape(product["output_type"])} · <strong>人工投入：</strong>{html.escape(product.get("manual_effort_level", "unknown"))}</p><p>{html.escape(product.get("notes", ""))}</p><h3>来源与归属</h3><ul class="sources">{source_items}</ul><p class="muted">仅作引用、归纳与独立评测；原作品及商标权利归相应权利人。来源标注不代表原作者认可本项目。</p></section>'
    body += "".join(appearances) or '<div class="card"><p>该对象尚无统一任务下的评测证据。</p></div>'
    return _page(product["name"], body)


def _methods_page(workflows: list[dict[str, Any]]) -> str:
    cards = []
    for workflow in sorted(workflows, key=lambda item: (item["status"] != "evaluated", item["name"])):
        components = sorted({step.get("component") for step in workflow["steps"] if step.get("component")})
        searchable = " ".join([workflow["name"], workflow.get("input_type", ""), *components]).lower()
        tags = "".join(f'<span class="tag">{html.escape(item)}</span>' for item in components)
        cards.append(
            f'<article class="card method" data-status="{html.escape(workflow["status"])}" data-output="{html.escape(workflow["output_type"])}" data-effort="{html.escape(workflow.get("manual_effort_level", "unknown"))}" data-search="{html.escape(searchable)}"><h2><a href="{html.escape(workflow["workflow_id"])}.html">{html.escape(workflow["name"])}</a></h2><p>{html.escape(workflow.get("notes", ""))}</p><div class="method-meta"><span class="tag">{html.escape(workflow["status"])}</span><span class="tag">输出 {html.escape(workflow["output_type"])}</span><span class="tag">人工投入 {html.escape(workflow.get("manual_effort_level", "unknown"))}</span>{tags}</div></article>'
        )
    body = f'''<div class="hero"><h1>AI PPT 方法库</h1><p>把跨平台教程去重为可比较的工作流。documented 表示步骤已有来源支持，evaluated 才表示完成统一实测。</p></div>
    <div class="card filters"><input id="q" type="search" placeholder="搜索工具、方法或输入"><select id="status"><option value="">全部状态</option><option>discovered</option><option>documented</option><option>queued</option><option>evaluated</option></select><select id="output"><option value="">全部输出</option><option>pptx</option><option>web</option><option>images</option><option>pdf</option><option>mixed</option></select><select id="effort"><option value="">全部人工投入</option><option>low</option><option>medium</option><option>high</option><option>unknown</option></select><strong id="count">{len(cards)} 种方法</strong></div>
    <div id="methods">{"".join(cards)}</div><script>const cards=[...document.querySelectorAll('.method')],q=document.querySelector('#q'),s=document.querySelector('#status'),o=document.querySelector('#output'),e=document.querySelector('#effort'),count=document.querySelector('#count');function filter(){{let n=0;cards.forEach(c=>{{const ok=(!q.value||c.dataset.search.includes(q.value.toLowerCase()))&&(!s.value||c.dataset.status===s.value)&&(!o.value||c.dataset.output===o.value)&&(!e.value||c.dataset.effort===e.value);c.hidden=!ok;if(ok)n++}});count.textContent=n+' 种方法'}}[q,s,o,e].forEach(x=>x.addEventListener('input',filter));</script>'''
    return _page("AI PPT 方法库", body)


def _research_page(research: dict[str, Any]) -> str:
    rows = []
    for item in research.get("entries", []):
        rows.append(
            f'<tr data-route="{html.escape(item["route"])}" data-priority="{html.escape(item["test_priority"])}"><td><a href="{html.escape(item["url"])}"><strong>{html.escape(item["name"])}</strong></a></td><td>{html.escape(item["route"])}</td><td>{html.escape(", ".join(item["inputs"]))}</td><td>{html.escape(", ".join(item["outputs"]))}</td><td>{html.escape(item["access"])}</td><td>{html.escape(item["evidence"])}</td><td>{html.escape(item["test_priority"])}</td></tr>'
        )
    routes = sorted({item["route"] for item in research.get("entries", [])})
    options = "".join(f'<option>{html.escape(route)}</option>' for route in routes)
    body = f'''<div class="hero"><h1>AI PPT 工具与路线全景</h1><p>截至 {html.escape(research["as_of"])} 的版本化长名单。收录表示进入调研范围，不代表通过实测。</p></div><div class="card"><p><strong>{len(rows)} 个候选对象</strong>，覆盖原生办公、独立生成器、设计平台、多工具流水线、代码生成和论文转演示。<a href="https://github.com/undefinted/decksignal/blob/main/docs/landscape-report-2026-09.md">阅读完整调研报告</a></p><div class="filters"><select id="route"><option value="">全部路线</option>{options}</select><select id="priority"><option value="">全部优先级</option><option>P0</option><option>P1</option><option>P2</option></select><strong id="research-count">{len(rows)} 个候选</strong></div></div><div style="overflow:auto"><table><thead><tr><th>工具/方法</th><th>路线</th><th>输入</th><th>输出</th><th>访问</th><th>证据</th><th>队列</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div><script>const rr=[...document.querySelectorAll('tbody tr')],route=document.querySelector('#route'),priority=document.querySelector('#priority'),rc=document.querySelector('#research-count');function rf(){{let n=0;rr.forEach(x=>{{const ok=(!route.value||x.dataset.route===route.value)&&(!priority.value||x.dataset.priority===priority.value);x.hidden=!ok;if(ok)n++}});rc.textContent=n+' 个候选'}}[route,priority].forEach(x=>x.addEventListener('input',rf));</script>'''
    return _page("AI PPT 工具与路线全景", body)


def _benchmark_rows(board: dict[str, Any]) -> str:
    if not board.get("rows"):
        return '<div class="empty">尚未导入该 benchmark 的可发布实测结果。</div>'
    rows = "".join(
        f'<tr><td>{row["rank"]}</td><td><a href="{html.escape(row["subject_id"])}.html">{html.escape(row["product"])}</a></td><td class="score">{row["score"]:.1f}</td><td>{row["evidence_count"]}</td><td>{html.escape("、".join(row["capabilities"]))}</td></tr>'
        for row in board["rows"] if row["score"] is not None
    )
    return f'<table><thead><tr><th>#</th><th>对象</th><th>归一化分数</th><th>证据</th><th>覆盖能力</th></tr></thead><tbody>{rows}</tbody></table>'


def _benchmarks_page(registry: dict[str, Any], rankings: dict[str, Any]) -> str:
    result_boards = rankings.get("benchmark_leaderboards", {})
    sections = []
    for source in registry.get("sources", []):
        board = result_boards.get(source["name"], {"rows": []})
        capabilities = "、".join(source.get("capabilities", []))
        url = source.get("url")
        title = f'<a href="{html.escape(url)}">{html.escape(source["name"])}</a>' if url else html.escape(source["name"])
        sections.append(
            f'<section class="card" id="{html.escape(source["id"])}"><h2>{title}</h2><p>适配状态：<strong>{html.escape(source["adapter_status"])}</strong> · 覆盖：{html.escape(capabilities)}</p>{_benchmark_rows(board)}</section>'
        )
    body = f'<div class="hero"><h1>各 Benchmark 分榜</h1><p>保留每套 benchmark 的独立观察口径，避免用一个总分掩盖任务差异。分数只有在真实证据导入后才显示。</p></div>{"".join(sections)}'
    return _page("Benchmark 分榜", body)


def build_site(
    rankings_path: str | Path,
    products_path: str | Path,
    output_dir: str | Path,
    *,
    workflows_path: str | Path | None = None,
    sources_path: str | Path | None = None,
    research_path: str | Path | None = None,
    benchmarks_path: str | Path | None = None,
) -> dict[str, Any]:
    rankings = json.loads(Path(rankings_path).read_text(encoding="utf-8"))
    product_records = load_json_records(products_path)
    subjects = {
        record["product_id"]: {**record, "subject_kind": "product"}
        for record in latest_product_snapshots(product_records).values()
    }
    if workflows_path is not None:
        workflow_records = load_json_records(workflows_path)
        latest_workflows = list(latest_snapshots(workflow_records, "workflow_id").values())
        subjects.update(
            {
                record["workflow_id"]: {**record, "subject_kind": "workflow"}
                for record in latest_workflows
            }
        )
    else:
        latest_workflows = []
    sources: dict[str, dict[str, Any]] = {}
    if sources_path is not None:
        catalog = json.loads(Path(sources_path).read_text(encoding="utf-8"))
        sources = {item["source_id"]: item for item in catalog["sources"]}
        known_refs = set(sources) | {item["url"] for item in sources.values()}
        unresolved = sorted(
            {ref for workflow in latest_workflows for ref in workflow.get("source_refs", []) if ref not in known_refs}
        )
        if unresolved:
            raise ValueError("Unresolved workflow source references: " + ", ".join(unresolved))
    output = Path(output_dir)
    (output / "assets").mkdir(parents=True, exist_ok=True)
    (output / "assets" / "style.css").write_text(STYLE.strip() + "\n", encoding="utf-8")
    (output / "rankings.json").write_text(json.dumps(rankings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    boards = rankings["leaderboards"]
    tabs = "".join(f'<a href="#{html.escape(key)}">{html.escape(board["label_zh"])}</a>' for key, board in boards.items())
    sections = "".join(f'<section id="{html.escape(key)}"><h2>{html.escape(board["label_zh"])}</h2>{_board_table(board)}</section>' for key, board in boards.items())
    research = {"as_of": "未提供", "entries": []}
    if research_path is not None:
        research = json.loads(Path(research_path).read_text(encoding="utf-8"))
    benchmark_registry = {"sources": []}
    if benchmarks_path is not None:
        benchmark_registry = yaml.safe_load(Path(benchmarks_path).read_text(encoding="utf-8"))
    scored_rows = sum(
        1 for board in boards.values() for row in board["rows"] if row.get("eligible")
    )
    benchmark_count = len(benchmark_registry.get("sources", []))
    status = '<section class="card notice"><strong>榜单状态：等待首批真实实测</strong><p>当前没有对象达到正式排名的证据门槛，因此不展示虚构分数。工具目录和方法收录不等于能力成绩。</p></section>' if scored_rows == 0 else ""
    kpis = f'<div class="grid"><div class="card"><span class="kpi">{len(research.get("entries", []))}</span>候选工具与路线</div><div class="card"><span class="kpi">{len(latest_workflows)}</span>去重方法</div><div class="card"><span class="kpi">{benchmark_count}</span>已接入/跟踪 Benchmark</div><div class="card"><span class="kpi">{scored_rows}</span>当前有效榜单记录</div></div>'
    body = f'<div class="hero"><h1>看见工具之外的真实能力</h1><p>DeckSignal 聚合独立 benchmark、可复现评测和盲评证据，呈现 AI 演示工具与方法的分数、覆盖度和证据状态。</p></div>{kpis}{status}<div class="card"><h2>如何判断制作水平</h2><p>内容忠实度 · 叙事结构 · 视觉设计 · 指令遵循 · 原生可编辑性 · 导出还原度 · 稳定性 · 后续编辑 · 中文能力 · 成本价值</p><p><a href="benchmarks.html">查看各 Benchmark 分榜与适配状态 →</a></p></div><nav class="tabs">{tabs}</nav>{sections}'
    (output / "index.html").write_text(_page("AI 演示能力动态榜", body), encoding="utf-8")
    (output / "methods.html").write_text(_methods_page(latest_workflows), encoding="utf-8")
    (output / "research.html").write_text(_research_page(research), encoding="utf-8")
    (output / "benchmarks.html").write_text(_benchmarks_page(benchmark_registry, rankings), encoding="utf-8")

    subject_ids_written: set[str] = set()
    for subject_id, snapshot in subjects.items():
        (output / f"{subject_id}.html").write_text(
            _product_page(snapshot, boards, sources), encoding="utf-8"
        )
        subject_ids_written.add(subject_id)
    return {
        "output": str(output),
        "pages": 4 + len(subject_ids_written),
        "subjects": len(subject_ids_written),
        "products": len(
            [item for item in subjects.values() if item["subject_kind"] == "product"]
        ),
        "workflows": len(
            [item for item in subjects.values() if item["subject_kind"] == "workflow"]
        ),
        "leaderboards": len(boards),
    }
