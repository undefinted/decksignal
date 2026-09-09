$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param([scriptblock]$Command)
    & $Command
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

Invoke-Checked { python -m pytest }
Invoke-Checked { ruff check src tests }
Invoke-Checked { openpptbench validate benchmark/tasks }
Invoke-Checked { openpptbench validate data/products --schema benchmark/schema/product-snapshot.schema.json }
Invoke-Checked { openpptbench validate data/recommendations --schema benchmark/schema/recommendation-source.schema.json }
Invoke-Checked { openpptbench rank data/evidence --products data/products --workflows data/workflows --config benchmark/config/capabilities-v0.2.yaml --output public/rankings.json }
Invoke-Checked { openpptbench build-site public/rankings.json --products data/products --workflows data/workflows --output-dir public/site }

Write-Host "Build complete: public/site/index.html"
