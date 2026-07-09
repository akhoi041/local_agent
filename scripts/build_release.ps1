param(
  [switch]$AllowDirty
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
Set-Location $root
$ErrorActionPreference = "Stop"

function Get-Slug([string]$value) {
  return ($value.Trim().ToLowerInvariant() -replace '[^a-z0-9]+', '-').Trim('-')
}

function Assert-CleanTree {
  if ($AllowDirty) {
    Write-Warning "Release build is running with -AllowDirty. Do not use this for public distribution."
    return
  }
  $git = Get-Command git -ErrorAction SilentlyContinue
  if (-not $git) {
    throw "git was not found; cannot verify that the source tree is clean."
  }
  $status = git status --porcelain
  if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE"
  }
  if ($status) {
    throw "Release build requires a clean git tree. Commit/stash changes or rerun with -AllowDirty for local validation only."
  }
}

function Reset-Directory([string]$path) {
  $rootPath = (Resolve-Path -LiteralPath $root).Path
  if (Test-Path -LiteralPath $path) {
    $targetPath = (Resolve-Path -LiteralPath $path).Path
    if (-not $targetPath.StartsWith($rootPath)) {
      throw "Refusing to remove path outside workspace: $targetPath"
    }
    Remove-Item -LiteralPath $targetPath -Recurse -Force
  }
  New-Item -ItemType Directory -Path $path -Force | Out-Null
}

Assert-CleanTree

$identityPath = Join-Path $root "config\app_identity.json"
$identity = Get-Content -LiteralPath $identityPath -Raw | ConvertFrom-Json
$appName = $identity.display_name
$channel = Get-Slug $identity.channel
$version = $identity.version
$releaseName = "$appName-$version-$channel"
$releaseRoot = Join-Path $root "releases"
$releaseDir = Join-Path $releaseRoot $releaseName

Reset-Directory $releaseDir

& (Join-Path $root "scripts\build_app.ps1")
if ($LASTEXITCODE -ne 0) {
  throw "App build failed with exit code $LASTEXITCODE"
}

$exePath = Join-Path $root "dist\$appName.exe"
if (-not (Test-Path -LiteralPath $exePath)) {
  throw "Expected executable was not built: $exePath"
}

$artifactPath = Join-Path $releaseDir "$releaseName.exe"
Copy-Item -LiteralPath $exePath -Destination $artifactPath -Force
Copy-Item -LiteralPath $identityPath -Destination (Join-Path $releaseDir "app_identity.json") -Force
Copy-Item -LiteralPath (Join-Path $root "config\signing_policy.json") -Destination (Join-Path $releaseDir "signing_policy.json") -Force
Copy-Item -LiteralPath (Join-Path $root "config\default_config.json") -Destination (Join-Path $releaseDir "default_config.json") -Force
Copy-Item -LiteralPath (Join-Path $root "docs\README.md") -Destination (Join-Path $releaseDir "README.md") -Force
$releaseDocsDir = Join-Path $releaseDir "docs"
New-Item -ItemType Directory -Path $releaseDocsDir -Force | Out-Null
foreach ($docName in @("LICENSE", "RELEASE_NOTES.md", "EULA.md", "PRIVACY.md", "THIRD_PARTY_NOTICES.md", "CODE_SIGNING.md", "INSTALLED_APP_SMOKE_TEST.md", "TALOS_RECOVERY_GUIDE.md", "TALOS_SUPPORT_DEBUG.md")) {
  Copy-Item -LiteralPath (Join-Path $root "docs\$docName") -Destination (Join-Path $releaseDocsDir $docName) -Force
}

$hash = Get-FileHash -LiteralPath $artifactPath -Algorithm SHA256
$manifest = [ordered]@{
  app_name = $appName
  publisher = $identity.publisher
  version = $version
  channel = $identity.channel
  release = $releaseName
  built_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss zzz")
  clean_tree_required = -not $AllowDirty
  artifacts = @(
    [ordered]@{
      file = Split-Path -Leaf $artifactPath
      type = "windows-executable"
      sha256 = $hash.Hash
      bytes = (Get-Item -LiteralPath $artifactPath).Length
    }
  )
}

$manifestPath = Join-Path $releaseDir "release_manifest.json"
$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $manifestPath -Encoding utf8

Write-Host "Release artifacts:"
Write-Host $releaseDir
Write-Host $artifactPath
Write-Host $manifestPath
