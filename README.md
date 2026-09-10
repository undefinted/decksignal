# DeckSignal

**Find the signal in AI presentations.**

DeckSignal（AI 演示智鉴）is an open presentation-intelligence project for AI presentation tools **and production workflows**. It continuously discovers products and online methods, runs or imports compatible benchmarks, preserves the evidence behind every result, and publishes versioned, scenario-aware rankings.

The current seed catalog contains **16 deduplicated workflows** sourced from Xiaohongshu, Bilibili, YouTube, official product documentation, and open-source repositories. The generated site includes a searchable method library. Cataloged tutorials are not treated as proven claims: only entries marked `evaluated` have completed the common test protocol.

DeckSignal is not intended to replace every presentation benchmark. Its internal evaluation engine, **OpenPPTBench**, provides the integration layer between benchmark projects, commercial products, multi-tool recipes, reproducible test runs, human preference studies, and users trying to choose the right way to make a deck.

## Principles

- **Reproducible:** prompts, settings, timestamps, artifacts, and scoring inputs are recorded.
- **Artifact-first:** both rendered slides and the native `.pptx` structure are evaluated.
- **Scenario-aware:** business, education, and product communication are reported separately.
- **Human-aligned:** automated checks support, rather than replace, blinded human comparison.
- **Versioned:** results identify the product, model, plan, configuration, and evaluation date.
- **Transparent:** raw measurements and aggregation logic are public.
- **Source-aware:** imported claims never become equivalent to first-party reproducible runs.
- **Time-aware:** rankings decay or become stale as fast-changing products are updated.
- **Coverage-aware:** a high score on one narrow test is not treated as broad product excellence.

## Current foundation

- 10 Chinese benchmark tasks across business, education, and product scenarios.
- A machine-readable submission manifest.
- Native PPTX inspection for structure, editability, overflow-risk, overlap-risk, typography, and media quality.
- A six-dimension expert rubric.
- A pairwise blind-review schema suitable for Elo or Bradley–Terry aggregation.
- A leaderboard builder that preserves dimension scores instead of hiding them behind one number.

The next release pivots this foundation into a continuous system with a tool registry, benchmark adapters, normalized evidence records, scheduled re-evaluation, and confidence-aware rankings. See [system design](docs/system-design.md).

## Quick start

Requirements: Python 3.10+ and LibreOffice (optional, for rendering in a later release).

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -e .[dev]

decksignal validate benchmark/tasks
decksignal inspect path/to/deck.pptx --output results/raw/deck.metrics.json
decksignal aggregate results/submissions.json --output results/leaderboard/leaderboard.json
pytest
```

On macOS/Linux, activate the environment with `source .venv/bin/activate`.

## Continuous-system commands

```bash
# Import a normalized export produced by an upstream benchmark adapter
decksignal import-csv upstream.csv \
  --source slidesgen-bench \
  --source-version <pinned-commit> \
  --output-dir data/evidence

# Build confidence-, coverage-, and freshness-aware rankings
decksignal rank data/evidence \
  --products data/products \
  --workflows data/workflows \
  --config benchmark/config/capabilities-v0.2.yaml \
  --output public/rankings.json

# Generate a static comparison site
decksignal build-site public/rankings.json \
  --products data/products \
  --workflows data/workflows \
  --sources data/sources/catalog-v0.1.json \
  --research data/research/landscape-v0.1.json \
  --benchmarks benchmark/sources/registry-v0.2.yaml \
  --output-dir public/site

# Monitor registered products and discover open-source candidates
decksignal check-products data/products --output monitoring-output/product-health.json
decksignal discover-github --query 'topic:ai-presentation' \
  --output monitoring-output/discoveries.json
```

Open `public/site/methods.html` to browse and filter methods by status, output format, and manual effort. Each detail page retains source links, normalized steps, inputs, outputs, and caveats.

Imported scores affect a leaderboard only when their normalized mapping, provenance, product snapshot, and evidence coverage satisfy that leaderboard's published policy.

## A valid evaluation run

The main track uses the following protocol:

1. Use the exact published task prompt and assets.
2. Use the product's default generation mode unless the task specifies otherwise.
3. Allow one generation attempt; rerun only after a documented technical failure.
4. Do not manually edit the output.
5. Record product, model/version if exposed, plan, settings, start/end time, and failure notes.
6. Preserve the original output and render all slides for blind review.
7. Publish automatic measurements separately from human judgments.

See [the methodology](docs/methodology.md) and [reproducibility protocol](docs/reproducibility.md).
The first real-world execution is defined in the [pilot runbook](docs/pilot-runbook.md), with candidates in `benchmark/products/candidates-v0.1.yaml`.

## Repository layout

```text
benchmark/          Versioned tasks, rubrics, and schemas
src/openpptbench/   OpenPPTBench evaluation engine and DeckSignal CLI
tests/              Unit and integration tests
results/            Raw and normalized evaluation outputs
docs/               Methodology and contribution documentation
website/            Placeholder for the public comparison UI
```

## What the benchmark does not claim

DeckSignal does not claim that one product is universally “best.” Rankings depend on scenario, product version, plan, locale, and evaluation date. Automated visual heuristics are diagnostic signals, not aesthetic truth.

## License

Code is released under the Apache License 2.0. Benchmark task text and original metadata are released under CC BY 4.0. Third-party submitted artifacts retain their original rights and may have separate redistribution restrictions.
