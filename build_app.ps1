$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$ErrorActionPreference = "Stop"

$appName = "Talos"

python -m PyInstaller `
  --noconfirm `
  --windowed `
  --onefile `
  --name $appName `
  --add-data "web_frontend;web_frontend" `
  --clean `
  desktop_app.py

if ($LASTEXITCODE -ne 0) {
  throw "PyInstaller build failed with exit code $LASTEXITCODE"
}

$distDir = Join-Path $root "dist"
$exePath = Join-Path $distDir "$appName.exe"
if (-not (Test-Path -LiteralPath $exePath)) {
  throw "Build output was not created: $exePath"
}

Write-Host "Built app:"
Write-Host $exePath
