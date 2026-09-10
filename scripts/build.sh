#!/usr/bin/env bash
set -euo pipefail

python -m pytest
ruff check src tests
decksignal validate benchmark/tasks
decksignal validate data/products --schema benchmark/schema/product-snapshot.schema.json
decksignal validate data/recommendations --schema benchmark/schema/recommendation-source.schema.json
decksignal validate data/workflows --schema benchmark/schema/workflow-snapshot.schema.json
decksignal validate data/sources/catalog-v0.1.json --schema benchmark/schema/source-catalog.schema.json
decksignal rank data/evidence --products data/products --workflows data/workflows --config benchmark/config/capabilities-v0.2.yaml --output public/rankings.json
decksignal build-site public/rankings.json --products data/products --workflows data/workflows --sources data/sources/catalog-v0.1.json --research data/research/landscape-v0.1.json --benchmarks benchmark/sources/registry-v0.2.yaml --output-dir public/site

echo "Build complete: public/site/index.html"
