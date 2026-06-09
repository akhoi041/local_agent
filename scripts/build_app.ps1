$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
Set-Location $root
$ErrorActionPreference = "Stop"

$appName = "Talos"
$nativeDll = Join-Path $root "native\bin\talos_native.dll"

try {
  & (Join-Path $root "scripts\build_native.ps1")
} catch {
  Write-Warning "Native C library was not built: $($_.Exception.Message)"
}

$extraArgs = @()
if (Test-Path -LiteralPath $nativeDll) {
  $extraArgs += @("--add-binary", "native\bin\talos_native.dll;native\bin")
}

python -m PyInstaller `
  --noconfirm `
  --windowed `
  --onefile `
  --name $appName `
  --add-data "ui\web_frontend;web_frontend" `
  @extraArgs `
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
