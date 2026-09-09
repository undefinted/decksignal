#!/usr/bin/env bash
set -euo pipefail

python -m pytest
ruff check src tests
openpptbench validate benchmark/tasks
openpptbench validate data/products --schema benchmark/schema/product-snapshot.schema.json
openpptbench validate data/recommendations --schema benchmark/schema/recommendation-source.schema.json
openpptbench validate data/workflows --schema benchmark/schema/workflow-snapshot.schema.json
openpptbench validate data/sources/catalog-v0.1.json --schema benchmark/schema/source-catalog.schema.json
openpptbench rank data/evidence --products data/products --workflows data/workflows --config benchmark/config/capabilities-v0.2.yaml --output public/rankings.json
openpptbench build-site public/rankings.json --products data/products --workflows data/workflows --sources data/sources/catalog-v0.1.json --output-dir public/site

echo "Build complete: public/site/index.html"
