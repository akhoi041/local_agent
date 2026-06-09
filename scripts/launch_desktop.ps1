$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
$sourceApp = Join-Path $root "desktop_app.py"
if (Test-Path -LiteralPath $sourceApp) {
  Start-Process -FilePath python -ArgumentList '-B','desktop_app.py' -WorkingDirectory $root
  exit 0
}

$installed = Join-Path $env:LOCALAPPDATA "Programs\Talos\Talos.exe"
if (Test-Path -LiteralPath $installed) {
  Start-Process -FilePath $installed
  exit 0
}

Start-Process -FilePath python -ArgumentList '-B','desktop_app.py' -WorkingDirectory $root
