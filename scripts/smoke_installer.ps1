param(
  [switch]$AllowDirty,
  [switch]$SkipBuild
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
Set-Location $root
$ErrorActionPreference = "Stop"

function Get-Slug([string]$value) {
  return ($value.Trim().ToLowerInvariant() -replace '[^a-z0-9]+', '-').Trim('-')
}

function Invoke-ProcessChecked([string]$FilePath, [string[]]$ArgumentList, [string]$Label) {
  $process = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -Wait -PassThru -WindowStyle Hidden
  if ($process.ExitCode -ne 0) {
    throw "$Label failed with exit code $($process.ExitCode)"
  }
}

$identity = Get-Content -LiteralPath (Join-Path $root "config\app_identity.json") -Raw | ConvertFrom-Json
$appName = $identity.display_name
$releaseName = "$appName-$($identity.version)-$(Get-Slug $identity.channel)"
$releaseDir = Join-Path $root "releases\$releaseName"
$installerPath = Join-Path $releaseDir "$releaseName-setup.exe"

if (-not $SkipBuild) {
  & (Join-Path $root "scripts\build_installer.ps1") -AllowDirty:$AllowDirty
  if ($LASTEXITCODE -ne 0) {
    throw "Installer build failed with exit code $LASTEXITCODE"
  }
}

if (-not (Test-Path -LiteralPath $installerPath)) {
  throw "Installer was not found: $installerPath"
}

$smokeRoot = Join-Path ([System.IO.Path]::GetTempPath()) "TalosInstallerSmoke"
$installDir = Join-Path $smokeRoot $appName
$startMenuDir = Join-Path ([Environment]::GetFolderPath("Programs")) $appName
$startMenuShortcut = Join-Path $startMenuDir "$appName.lnk"

if (Test-Path -LiteralPath $installDir) {
  $oldUninstaller = Join-Path $installDir "unins000.exe"
  if (Test-Path -LiteralPath $oldUninstaller) {
    Invoke-ProcessChecked $oldUninstaller @("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART") "Previous uninstall"
  }
  if (Test-Path -LiteralPath $installDir) {
    Remove-Item -LiteralPath $installDir -Recurse -Force
  }
}

New-Item -ItemType Directory -Path $smokeRoot -Force | Out-Null
Invoke-ProcessChecked $installerPath @(
  "/VERYSILENT",
  "/SUPPRESSMSGBOXES",
  "/NORESTART",
  "/DIR=$installDir"
) "Silent install"

$installedExe = Join-Path $installDir "$appName.exe"
$uninstaller = Join-Path $installDir "unins000.exe"
$installedManifest = Join-Path $installDir "release_manifest.json"
$installedConfig = Join-Path $installDir "config\default_config.json"
$installedReleaseNotes = Join-Path $installDir "docs\RELEASE_NOTES.md"
$installedEula = Join-Path $installDir "docs\EULA.md"
$installedPrivacy = Join-Path $installDir "docs\PRIVACY.md"
$installedThirdParty = Join-Path $installDir "docs\THIRD_PARTY_NOTICES.md"
$installedCodeSigning = Join-Path $installDir "docs\CODE_SIGNING.md"
$installedAppSmokeDoc = Join-Path $installDir "docs\INSTALLED_APP_SMOKE_TEST.md"
$userConfig = Join-Path $installDir "config\config.json"
$releaseNotesShortcut = Join-Path $startMenuDir "Release Notes.lnk"

foreach ($path in @($installedExe, $uninstaller, $installedManifest, $installedConfig, $installedReleaseNotes, $installedEula, $installedPrivacy, $installedThirdParty, $installedCodeSigning, $installedAppSmokeDoc, $startMenuShortcut, $releaseNotesShortcut)) {
  if (-not (Test-Path -LiteralPath $path)) {
    throw "Installer smoke test expected file was not created: $path"
  }
}
if (Test-Path -LiteralPath $userConfig) {
  throw "Installer smoke test found a writable runtime config inside the install directory: $userConfig"
}

Invoke-ProcessChecked $uninstaller @("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART") "Silent uninstall"

foreach ($path in @($installedExe, $uninstaller, $installedManifest, $installedConfig, $installedReleaseNotes, $installedEula, $installedPrivacy, $installedThirdParty, $installedCodeSigning, $installedAppSmokeDoc, $startMenuShortcut, $releaseNotesShortcut)) {
  if (Test-Path -LiteralPath $path) {
    throw "Installer smoke test expected file was not removed: $path"
  }
}

if (Test-Path -LiteralPath $installDir) {
  $remaining = Get-ChildItem -LiteralPath $installDir -Force -ErrorAction SilentlyContinue
  if ($remaining) {
    throw "Installer smoke test left files in install directory: $installDir"
  }
  Remove-Item -LiteralPath $installDir -Force
}

if (Test-Path -LiteralPath $smokeRoot) {
  $remaining = Get-ChildItem -LiteralPath $smokeRoot -Force -ErrorAction SilentlyContinue
  if (-not $remaining) {
    Remove-Item -LiteralPath $smokeRoot -Force
  }
}

Write-Host "Installer smoke test passed:"
Write-Host $installerPath
