param([string]$InputRoot = "results/raw/pilot-control", [string]$OutputRoot = "results/raw/pilot-control/rendered")
$soffice = @("C:\Program Files\LibreOffice\program\soffice.exe", "C:\Program Files (x86)\LibreOffice\program\soffice.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $soffice) { throw "LibreOffice was not found. Install it, then rerun this script." }
New-Item -ItemType Directory -Force $OutputRoot | Out-Null
Get-ChildItem -Path $InputRoot -Filter *.pptx -Recurse | ForEach-Object { & $soffice --headless --convert-to pdf --outdir $OutputRoot $_.FullName; if ($LASTEXITCODE -ne 0) { throw "LibreOffice failed for $($_.FullName)" } }
Write-Output "Rendered PPTX files from $InputRoot to $OutputRoot"
