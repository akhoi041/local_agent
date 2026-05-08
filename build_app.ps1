$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$ErrorActionPreference = "Stop"

$appName = "LocalAgentDesktop"

python -m PyInstaller `
  --noconfirm `
  --windowed `
  --name $appName `
  --clean `
  desktop_app.py

if ($LASTEXITCODE -ne 0) {
  throw "PyInstaller build failed with exit code $LASTEXITCODE"
}

$distDir = Join-Path $root "dist\$appName"
if (-not (Test-Path -LiteralPath $distDir)) {
  throw "Build output was not created: $distDir"
}

Copy-Item -LiteralPath (Join-Path $root "config.json") -Destination (Join-Path $distDir "config.json") -Force
Copy-Item -LiteralPath (Join-Path $root "tasks.json") -Destination (Join-Path $distDir "tasks.json") -Force
Copy-Item -LiteralPath (Join-Path $root "README.md") -Destination (Join-Path $distDir "README.md") -Force

Write-Host "Built app:"
Write-Host (Join-Path $distDir "$appName.exe")
