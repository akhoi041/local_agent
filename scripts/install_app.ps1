$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
$identityPath = Join-Path $root "config\app_identity.json"
$identity = Get-Content -LiteralPath $identityPath -Raw | ConvertFrom-Json
$appName = $identity.display_name
$sourceExe = Join-Path $root "dist\$appName.exe"
$installDir = Join-Path $env:LOCALAPPDATA "Programs\$appName"
$installExe = Join-Path $installDir "$appName.exe"
$sourceIconDir = Join-Path $root $identity.icon_png_dir
$installIconDir = Join-Path $installDir $identity.icon_png_dir
$installIcon = Join-Path $installDir $identity.icon_ico

if (-not (Test-Path -LiteralPath $sourceExe)) {
  Write-Host "Build output not found. Run .\scripts\build_app.ps1 first."
  exit 1
}

if (Test-Path -LiteralPath $installDir) {
  Remove-Item -LiteralPath $installDir -Recurse -Force
}

New-Item -ItemType Directory -Path $installDir -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $installDir "config") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $installDir "docs") -Force | Out-Null
New-Item -ItemType Directory -Path $installIconDir -Force | Out-Null
Copy-Item -LiteralPath $sourceExe -Destination $installExe -Force
Copy-Item -LiteralPath (Join-Path $root "config\default_config.json") -Destination (Join-Path $installDir "config\default_config.json") -Force
Copy-Item -LiteralPath $identityPath -Destination (Join-Path $installDir "config\app_identity.json") -Force
Copy-Item -LiteralPath (Join-Path $sourceIconDir "*") -Destination $installIconDir -Force
Copy-Item -LiteralPath (Join-Path $root "docs\README.md") -Destination (Join-Path $installDir "README.md") -Force
foreach ($docName in @("LICENSE", "RELEASE_NOTES.md", "EULA.md", "PRIVACY.md", "THIRD_PARTY_NOTICES.md", "CODE_SIGNING.md", "DISTRIBUTION_COPY.md", "INSTALLED_APP_SMOKE_TEST.md", "TALOS_USER_GUIDE.md", "TALOS_FIRST_RUN_CHECKLIST.md", "TALOS_TROUBLESHOOTING.md", "TALOS_DIAGNOSTICS.md", "TALOS_INSTALL_LIFECYCLE.md", "TALOS_UI_UX_CHECKLIST.md", "TALOS_RECOVERY_GUIDE.md", "TALOS_SUPPORT_DEBUG.md")) {
  Copy-Item -LiteralPath (Join-Path $root "docs\$docName") -Destination (Join-Path $installDir "docs\$docName") -Force
}

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "$appName.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $installExe
$shortcut.WorkingDirectory = $installDir
$shortcut.Description = $identity.display_name
if (Test-Path -LiteralPath $installIcon) {
  $shortcut.IconLocation = $installIcon
}
$shortcut.Save()

Write-Host "Installed:"
Write-Host $installExe
Write-Host "Shortcut:"
Write-Host $shortcutPath
