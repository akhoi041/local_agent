$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
Set-Location $root
$ErrorActionPreference = "Stop"

$identityPath = Join-Path $root "config\app_identity.json"
$identity = Get-Content -LiteralPath $identityPath -Raw | ConvertFrom-Json
$appName = $identity.display_name
$iconPath = Join-Path $root $identity.icon_ico
$nativeDll = Join-Path $root "native\bin\talos_native.dll"
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$python = if (Test-Path -LiteralPath $venvPython) { $venvPython } else { "python" }

& $python -B (Join-Path $root "scripts\build_icons.py")
if ($LASTEXITCODE -ne 0) {
  throw "Icon build failed with exit code $LASTEXITCODE"
}

try {
  & (Join-Path $root "scripts\build_native.ps1")
} catch {
  Write-Warning "Native C library was not built: $($_.Exception.Message)"
}

$extraArgs = @()
if (Test-Path -LiteralPath $nativeDll) {
  $extraArgs += @("--add-binary", "native\bin\talos_native.dll;native\bin")
}
if (Test-Path -LiteralPath $iconPath) {
  $extraArgs += @("--icon", $iconPath)
}

& $python -m PyInstaller `
  --noconfirm `
  --windowed `
  --onefile `
  --name $appName `
  --add-data "ui\web_frontend;web_frontend" `
  --add-data "config\app_identity.json;config" `
  --add-data "config\default_config.json;config" `
  --add-data "assets\icons;assets\icons" `
  --add-data "docs\README.md;docs" `
  --add-data "scripts\clean_runtime.ps1;scripts" `
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
