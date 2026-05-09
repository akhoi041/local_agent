$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$installed = Join-Path $env:LOCALAPPDATA "Programs\LocalAgentDesktop\LocalAgentDesktop.exe"
if (Test-Path -LiteralPath $installed) {
  Start-Process -FilePath $installed
  exit 0
}

Start-Process -FilePath python -ArgumentList '-B','desktop_app.py' -WorkingDirectory $root
