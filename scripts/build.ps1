$ErrorActionPreference = "Stop"
$ProjectPython = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }

function Invoke-Checked {
    param([scriptblock]$Command)
    & $Command
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

Invoke-Checked { & $ProjectPython -m pytest }
Invoke-Checked { & $ProjectPython -m ruff check src tests }
Invoke-Checked { & $ProjectPython -m openpptbench.cli validate benchmark/tasks }
Invoke-Checked { & $ProjectPython -m openpptbench.cli validate data/products --schema benchmark/schema/product-snapshot.schema.json }
Invoke-Checked { & $ProjectPython -m openpptbench.cli validate data/recommendations --schema benchmark/schema/recommendation-source.schema.json }
Invoke-Checked { & $ProjectPython -m openpptbench.cli validate data/workflows --schema benchmark/schema/workflow-snapshot.schema.json }
Invoke-Checked { & $ProjectPython -m openpptbench.cli rank data/evidence --products data/products --workflows data/workflows --config benchmark/config/capabilities-v0.2.yaml --output public/rankings.json }
Invoke-Checked { & $ProjectPython -m openpptbench.cli build-site public/rankings.json --products data/products --workflows data/workflows --output-dir public/site }

Write-Host "Build complete: public/site/index.html"
