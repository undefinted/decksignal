param([string]$InputRoot = "submissions/pilot", [string]$OutputRoot = "results/raw/rendered")
$ErrorActionPreference = 'Stop'
$soffice = @("C:\Program Files\LibreOffice\program\soffice.exe", "C:\Program Files (x86)\LibreOffice\program\soffice.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $soffice) { throw "LibreOffice was not found. Install it, then rerun this script." }
$sourceRoot = (Resolve-Path -LiteralPath $InputRoot).Path
$destinationRoot = [System.IO.Path]::GetFullPath($OutputRoot)
$decks = @(Get-ChildItem -LiteralPath $sourceRoot -Filter *.pptx -Recurse -File)
if ($decks.Count -eq 0) { throw "No PPTX artifacts found in $sourceRoot" }
foreach ($deck in $decks) {
  $relativeFolder = $deck.DirectoryName.Substring($sourceRoot.Length).TrimStart([char]'\')
  $destination = Join-Path $destinationRoot $relativeFolder
  New-Item -ItemType Directory -Force -Path $destination | Out-Null
  $pdfPath = Join-Path $destination ($deck.BaseName + '.pdf')
  if (Test-Path -LiteralPath $pdfPath) { throw "Output already exists: $pdfPath. Select a fresh output directory." }
  $profilePath = Join-Path ([System.IO.Path]::GetTempPath()) ('decksignal-lo-' + [guid]::NewGuid())
  $profileUri = ([uri]$profilePath).AbsoluteUri
  $arguments = @('"-env:UserInstallation=' + $profileUri + '"', '--headless', '--convert-to', 'pdf', '--outdir', ('"' + $destination + '"'), ('"' + $deck.FullName + '"'))
  $process = Start-Process -FilePath $soffice -ArgumentList $arguments -WindowStyle Hidden -PassThru
  if (-not $process.WaitForExit(120000)) { $process.Kill(); throw "Rendering timed out: $($deck.FullName)" }
  if ($process.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $pdfPath)) { throw "PDF conversion failed: $($deck.FullName)" }
  if ((Get-Item -LiteralPath $pdfPath).Length -eq 0) { throw "Empty PDF: $pdfPath" }
  Write-Output $pdfPath
}
Write-Output "Rendered $($decks.Count) artifacts."
