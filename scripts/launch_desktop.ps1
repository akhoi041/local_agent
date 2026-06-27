$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
$sourceApp = Join-Path $root "desktop_app.py"
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$python = if (Test-Path -LiteralPath $venvPython) { $venvPython } else { "python" }

function Test-PyWebView {
  param([string]$PythonPath)
  & $PythonPath -B -c "import webview" *> $null
  return $LASTEXITCODE -eq 0
}

if (Test-Path -LiteralPath $sourceApp) {
  if (-not (Test-PyWebView $python)) {
    Write-Host "pywebview is missing for $python."
    Write-Host "Run: python -m pip install -r config\requirements.txt"
    exit 1
  }
  Start-Process -FilePath $python -ArgumentList '-B','desktop_app.py' -WorkingDirectory $root
  exit 0
}

$installed = Join-Path $env:LOCALAPPDATA "Programs\Talos\Talos.exe"
if (Test-Path -LiteralPath $installed) {
  Start-Process -FilePath $installed
  exit 0
}

if (-not (Test-PyWebView $python)) {
  Write-Host "pywebview is missing for $python."
  Write-Host "Run: python -m pip install -r config\requirements.txt"
  exit 1
}
Start-Process -FilePath $python -ArgumentList '-B','desktop_app.py' -WorkingDirectory $root
