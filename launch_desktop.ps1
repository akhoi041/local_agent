$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Start-Process -FilePath python -ArgumentList '-B','desktop_app.py' -WorkingDirectory $root
