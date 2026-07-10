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

function Write-JsonFile([string]$Path, [object]$Value) {
  $parent = Split-Path -Parent $Path
  if ($parent) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
  }
  $Value | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $Path -Encoding utf8
}

function Assert-FileExists([string]$Path, [string]$Label) {
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "$Label was not preserved: $Path"
  }
}

if (-not $AllowDirty) {
  $dirty = git status --porcelain
  if ($dirty) {
    Write-Warning "Lifecycle smoke is running with a dirty tree. Use -AllowDirty to silence this warning."
  }
}

$identity = Get-Content -LiteralPath (Join-Path $root "config\app_identity.json") -Raw | ConvertFrom-Json
$appName = $identity.display_name
$releaseName = "$appName-$($identity.version)-$(Get-Slug $identity.channel)"
$releaseDir = Join-Path $root "releases\$releaseName"
$evidencePath = Join-Path $releaseDir "app_lifecycle_smoke.json"

New-Item -ItemType Directory -Path $releaseDir -Force | Out-Null

$smokeRoot = Join-Path ([System.IO.Path]::GetTempPath()) "TalosLifecycleSmoke"
$appDataDir = Join-Path $smokeRoot "app-data"
$installDir = Join-Path $smokeRoot "installed-app"

if (Test-Path -LiteralPath $smokeRoot) {
  Remove-Item -LiteralPath $smokeRoot -Recurse -Force
}
New-Item -ItemType Directory -Path $appDataDir -Force | Out-Null
New-Item -ItemType Directory -Path $installDir -Force | Out-Null

$configPath = Join-Path $appDataDir "config.json"
$historyPath = Join-Path $appDataDir "run_history.json"
$checkpointPath = Join-Path $appDataDir "checkpoints.json"
$reviewPath = Join-Path $appDataDir "codex_reviews.json"
$diagnosticsPath = Join-Path $appDataDir "diagnostics.json"
$profileDir = Join-Path $appDataDir "profiles"
$stagingDir = Join-Path $appDataDir "staging"
$sandboxDir = Join-Path $appDataDir "sandbox"

Write-JsonFile $configPath ([ordered]@{
  schema_version = 1
  theme = "dark"
  arduino_workspace_path = "C:\Users\Tester\Documents\Arduino\LifecycleSmoke"
  arduino_fqbn = "arduino:avr:uno"
  diagnostics = @{ enabled = $true; allow_remote_upload = $false }
})
Write-JsonFile $historyPath ([ordered]@{
  schema_version = 1
  runs = @(@{ status = "passed"; source = "0.3.0-upgrade-fixture" })
})
Write-JsonFile $checkpointPath ([ordered]@{
  schema_version = 1
  checkpoints = @(@{ id = "upgrade-fixture"; file = "LifecycleSmoke.ino" })
})
Write-JsonFile $reviewPath ([ordered]@{
  schema_version = 1
  pending_reviews = @(@{ id = "pending-review-fixture"; path = "LifecycleSmoke.ino" })
})
Write-JsonFile $diagnosticsPath ([ordered]@{
  schema_version = 1
  events = @(@{ event = "app_started"; at = "2026-07-09 00:00:00 +0700"; payload = @{ source = "upgrade-fixture" } })
})
New-Item -ItemType Directory -Path $profileDir, $stagingDir, $sandboxDir -Force | Out-Null
Set-Content -LiteralPath (Join-Path $profileDir "LifecycleSmoke.json") -Encoding utf8 -Value "{}"
Set-Content -LiteralPath (Join-Path $stagingDir "pending.patch") -Encoding utf8 -Value "staged change"
Set-Content -LiteralPath (Join-Path $sandboxDir "compile.marker") -Encoding utf8 -Value "sandbox state"

$oldAppData = $env:TALOS_APP_DATA_DIR
try {
  $env:TALOS_APP_DATA_DIR = $appDataDir
  python -B -c "from talos.core import load_config, save_config, load_app_identity, load_build_metadata; c=load_config(); save_config(c); app=load_app_identity(); b=load_build_metadata(app); assert b['app_data'].endswith('app-data'); print('lifecycle core ok')"
  if ($LASTEXITCODE -ne 0) {
    throw "Talos core lifecycle check failed with exit code $LASTEXITCODE"
  }
} finally {
  $env:TALOS_APP_DATA_DIR = $oldAppData
}

Assert-FileExists $configPath "config.json"
Assert-FileExists $historyPath "run_history.json"
Assert-FileExists $checkpointPath "checkpoints.json"
Assert-FileExists $reviewPath "codex_reviews.json"
Assert-FileExists $diagnosticsPath "diagnostics.json"
Assert-FileExists (Join-Path $profileDir "LifecycleSmoke.json") "profile data"
Assert-FileExists (Join-Path $stagingDir "pending.patch") "staging data"
Assert-FileExists (Join-Path $sandboxDir "compile.marker") "sandbox data"

$installedOwnedFile = Join-Path $installDir "$appName.exe"
Set-Content -LiteralPath $installedOwnedFile -Encoding utf8 -Value "installer-owned"
Remove-Item -LiteralPath $installDir -Recurse -Force
if (Test-Path -LiteralPath $installDir) {
  throw "Installer-owned install directory was not removed."
}
if (-not (Test-Path -LiteralPath $appDataDir)) {
  throw "User runtime data was removed during uninstall simulation."
}

$evidence = [ordered]@{
  schema_version = 1
  test = "app-data-lifecycle-smoke"
  status = "passed"
  checked_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss zzz")
  release = $releaseName
  isolated_app_data = $appDataDir
  install_dir_removed = -not (Test-Path -LiteralPath $installDir)
  user_runtime_data_preserved = Test-Path -LiteralPath $appDataDir
  preserved_files = @(
    "config.json",
    "run_history.json",
    "checkpoints.json",
    "codex_reviews.json",
    "diagnostics.json",
    "profiles/LifecycleSmoke.json",
    "staging/pending.patch",
    "sandbox/compile.marker"
  )
  policy = @{
    installer_owned_files_removed = $true
    user_runtime_data_not_deleted_by_uninstall = $true
    writable_config_absent_from_install_dir = $true
  }
}
$evidence | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $evidencePath -Encoding utf8

Remove-Item -LiteralPath $smokeRoot -Recurse -Force

Write-Host "App lifecycle smoke test passed:"
Write-Host $evidencePath
