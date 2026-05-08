$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$appName = "LocalAgentDesktop"
$source = Join-Path $root "dist\$appName"
$installDir = Join-Path $env:LOCALAPPDATA "Programs\$appName"

if (-not (Test-Path -LiteralPath (Join-Path $source "$appName.exe"))) {
  Write-Host "Build output not found. Run .\build_app.ps1 first."
  exit 1
}

if (Test-Path -LiteralPath $installDir) {
  Remove-Item -LiteralPath $installDir -Recurse -Force
}

New-Item -ItemType Directory -Path $installDir -Force | Out-Null
Copy-Item -Path (Join-Path $source "*") -Destination $installDir -Recurse -Force

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "$appName.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = Join-Path $installDir "$appName.exe"
$shortcut.WorkingDirectory = $installDir
$shortcut.Description = "Local Agent Desktop"
$shortcut.Save()

Write-Host "Installed:"
Write-Host (Join-Path $installDir "$appName.exe")
Write-Host "Shortcut:"
Write-Host $shortcutPath
