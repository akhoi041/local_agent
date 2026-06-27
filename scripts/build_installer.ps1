param(
  [switch]$AllowDirty,
  [switch]$SkipReleaseBuild
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
Set-Location $root
$ErrorActionPreference = "Stop"

function Get-Slug([string]$value) {
  return ($value.Trim().ToLowerInvariant() -replace '[^a-z0-9]+', '-').Trim('-')
}

function Find-InnoCompiler {
  $command = Get-Command ISCC.exe -ErrorAction SilentlyContinue
  if ($command) {
    return $command.Source
  }
  $candidates = @(
    (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"),
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe"
  )
  foreach ($candidate in $candidates) {
    if ($candidate -and (Test-Path -LiteralPath $candidate)) {
      return $candidate
    }
  }
  throw "Inno Setup compiler was not found. Install Inno Setup 6 or add ISCC.exe to PATH."
}

$identityPath = Join-Path $root "config\app_identity.json"
$identity = Get-Content -LiteralPath $identityPath -Raw | ConvertFrom-Json
$appName = $identity.display_name
$publisher = $identity.publisher
$version = $identity.version
$channel = $identity.channel
$releaseName = "$appName-$version-$(Get-Slug $channel)"
$releaseDir = Join-Path $root "releases\$releaseName"
$issPath = Join-Path $root "installer\talos.iss"
$iconPath = Join-Path $root $identity.icon_ico
$iscc = Find-InnoCompiler

if (-not $SkipReleaseBuild) {
  & (Join-Path $root "scripts\build_release.ps1") -AllowDirty:$AllowDirty
  if ($LASTEXITCODE -ne 0) {
    throw "Release build failed with exit code $LASTEXITCODE"
  }
}

$releaseExe = Join-Path $releaseDir "$releaseName.exe"
if (-not (Test-Path -LiteralPath $releaseExe)) {
  throw "Release executable was not found: $releaseExe"
}

$innoArgs = @(
  "/DMyAppName=$appName",
  "/DMyPublisher=$publisher",
  "/DMyVersion=$version",
  "/DMyChannel=$channel",
  "/DReleaseName=$releaseName",
  "/DReleaseDir=$releaseDir",
  "/DOutputDir=$releaseDir",
  "/DIconPath=$iconPath",
  $issPath
)

& $iscc @innoArgs
if ($LASTEXITCODE -ne 0) {
  throw "Installer build failed with exit code $LASTEXITCODE"
}

$installerPath = Join-Path $releaseDir "$releaseName-setup.exe"
if (-not (Test-Path -LiteralPath $installerPath)) {
  throw "Installer output was not created: $installerPath"
}

$manifestPath = Join-Path $releaseDir "release_manifest.json"
if (Test-Path -LiteralPath $manifestPath) {
  $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
  $hash = Get-FileHash -LiteralPath $installerPath -Algorithm SHA256
  $installerFile = Split-Path -Leaf $installerPath
  $artifacts = @(@($manifest.artifacts) | Where-Object { $_.file -ne $installerFile })
  $artifacts = @($artifacts) + @(
    [ordered]@{
      file = $installerFile
      type = "windows-installer"
      sha256 = $hash.Hash
      bytes = (Get-Item -LiteralPath $installerPath).Length
    }
  )
  $manifest | Add-Member -NotePropertyName installer_built_at -NotePropertyValue (Get-Date).ToString("yyyy-MM-dd HH:mm:ss zzz") -Force
  $manifest | Add-Member -NotePropertyName artifacts -NotePropertyValue $artifacts -Force
  $manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $manifestPath -Encoding utf8
}

Write-Host "Installer:"
Write-Host $installerPath
