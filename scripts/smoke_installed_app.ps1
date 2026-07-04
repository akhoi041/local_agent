param(
  [switch]$AllowDirty,
  [switch]$SkipBuild,
  [switch]$KeepInstalled,
  [switch]$SkipLaunch,
  [switch]$ManualArduinoConfirmed,
  [switch]$AutoArduinoHarness,
  [int]$TimeoutSec = 30
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

function Stop-InstalledTalos([object]$Process, [string]$InstallDir) {
  if ($Process -and -not $Process.HasExited) {
    Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
    Wait-Process -Id $Process.Id -Timeout 5 -ErrorAction SilentlyContinue
  }

  $escapedInstallDir = [System.IO.Path]::GetFullPath($InstallDir)
  Get-Process -Name $script:appName -ErrorAction SilentlyContinue |
    Where-Object {
      $_.Path -and [System.IO.Path]::GetFullPath($_.Path).StartsWith($escapedInstallDir)
    } |
    ForEach-Object {
      Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
      Wait-Process -Id $_.Id -Timeout 5 -ErrorAction SilentlyContinue
    }
}

function Remove-TreeWithRetry([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) {
    return
  }
  for ($attempt = 1; $attempt -le 8; $attempt++) {
    try {
      Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
      return
    } catch {
      if ($attempt -eq 8) {
        throw
      }
      Start-Sleep -Milliseconds (250 * $attempt)
    }
  }
}

function Wait-TalosHealth([int]$TimeoutSeconds) {
  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    foreach ($port in 8787..8806) {
      try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/health" -TimeoutSec 2
        if ($health -and $health.ok -and $health.service -eq $script:appName) {
          return [ordered]@{ port = $port; health = $health }
        }
      } catch {
      }
    }
    Start-Sleep -Milliseconds 500
  }
  throw "Timed out waiting for installed Talos /api/health."
}

function Write-SmokeEvidence([string]$Path, [hashtable]$Evidence) {
  $Evidence | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Path -Encoding utf8
}

function Invoke-TalosGet([int]$Port, [string]$Path) {
  return Invoke-RestMethod -Uri "http://127.0.0.1:$Port$Path" -TimeoutSec 10
}

function Invoke-TalosPost([int]$Port, [string]$Path, [hashtable]$Body) {
  $json = $Body | ConvertTo-Json -Depth 10
  return Invoke-RestMethod -Uri "http://127.0.0.1:$Port$Path" -Method Post -Body $json -ContentType "application/json; charset=utf-8" -TimeoutSec 120
}

function New-SmokeArduinoWorkspace([string]$Root) {
  $workspace = Join-Path $Root "arduino-workspace\TalosSmoke"
  New-Item -ItemType Directory -Path $workspace -Force | Out-Null
  $sketch = Join-Path $workspace "TalosSmoke.ino"
  @"
void setup() {
  Serial.begin(115200);
  Serial.println("talos smoke start");
}

void loop() {
  delay(1000);
}
"@ | Set-Content -LiteralPath $sketch -Encoding utf8
  return @{ workspace = $workspace; sketch = $sketch; relative = "TalosSmoke.ino" }
}

function Invoke-AutoArduinoHarness([int]$Port, [string]$Root) {
  $fixture = New-SmokeArduinoWorkspace $Root
  $workspace = $fixture.workspace
  $relative = $fixture.relative
  $fqbn = if ($env:TALOS_SMOKE_FQBN) { $env:TALOS_SMOKE_FQBN } else { "arduino:avr:uno" }

  $workspaceResult = Invoke-TalosPost $Port "/api/arduino_workspace" @{
    path = $workspace
    fqbn = $fqbn
  }
  if (-not $workspaceResult.ok) {
    throw "Auto harness could not configure Arduino workspace."
  }

  $profileResult = Invoke-TalosPost $Port "/api/arduino_profile" @{
    path = $workspace
    fqbn = $fqbn
    serial_port = "COM_TEST"
    baud_rate = 115200
    build_flags = @("-DTALOS_SMOKE=1")
    build_properties = @()
    libraries = @()
  }
  if (-not $profileResult.ok) {
    throw "Auto harness could not save Arduino profile."
  }

  $initial = Invoke-TalosGet $Port "/api/arduino_file?path=$relative"
  if (-not $initial.ok -or -not [string]$initial.content.Contains("talos smoke start")) {
    throw "Auto harness could not read the source file through Talos."
  }

  $talosEditContent = @"
void setup() {
  Serial.begin(115200);
  Serial.println("talos smoke start");
  Serial.println("edited by Talos");
}

void loop() {
  delay(1000);
}
"@
  $saveResult = Invoke-TalosPost $Port "/api/arduino_file" @{
    path = $relative
    content = $talosEditContent
  }
  if (-not $saveResult.ok) {
    throw "Auto harness could not save a Talos editor change."
  }

  $verifyBeforePatch = Invoke-TalosPost $Port "/api/arduino_verify" @{
    path = $workspace
    fqbn = $fqbn
    source = "installed_app_auto_harness"
  }

  $codexContent = @"
void setup() {
  Serial.begin(115200);
  Serial.println("talos smoke start");
  Serial.println("edited by Talos");
  Serial.println("changed by Codex smoke");
}

void loop() {
  delay(500);
}
"@
  $patchResult = Invoke-TalosPost $Port "/api/smoke/codex_patch" @{
    path = $relative
    content = $codexContent
  }
  if (-not $patchResult.ok) {
    throw "Auto harness could not stage a Codex smoke patch."
  }

  $patchId = [string]$patchResult.patch.id
  $applyResult = Invoke-TalosPost $Port "/api/codex_apply_patch" @{
    id = $patchId
    path = $relative
  }
  if (-not $applyResult.ok) {
    throw "Auto harness could not apply the Codex smoke patch to the Talos editor."
  }
  $editorContent = [string]$applyResult.file.editor_content
  if (-not $editorContent.Contains("changed by Codex smoke")) {
    throw "Applied Codex smoke patch did not produce editor content."
  }

  $savedBeforeCodexSave = Get-Content -LiteralPath $fixture.sketch -Raw
  if ($savedBeforeCodexSave.Contains("changed by Codex smoke")) {
    throw "Codex smoke patch wrote to the Arduino workspace before Save File."
  }

  $savePatchResult = Invoke-TalosPost $Port "/api/arduino_file" @{
    path = $relative
    content = $editorContent
  }
  if (-not $savePatchResult.ok) {
    throw "Auto harness could not save the applied Codex patch to the Arduino workspace."
  }

  $finalContent = Get-Content -LiteralPath $fixture.sketch -Raw
  if (-not $finalContent.Contains("changed by Codex smoke")) {
    throw "Arduino workspace did not receive the saved Codex smoke change."
  }

  $verifyAfterPatch = Invoke-TalosPost $Port "/api/arduino_verify" @{
    path = $workspace
    fqbn = $fqbn
    source = "installed_app_auto_harness"
  }

  return @{
    confirmed = $true
    workspace = $workspace
    file = $relative
    fqbn = $fqbn
    steps = @(
      "configure-temp-sketch-workspace",
      "save-environment-profile",
      "read-source-file",
      "edit-in-talos-and-save-file",
      "verify-sandbox",
      "stage-codex-smoke-patch",
      "apply-patch-to-talos-editor",
      "confirm-no-pre-save-workspace-write",
      "save-applied-patch-to-arduino-workspace",
      "verify-sandbox-again"
    )
    verify_before = @{
      ok = [bool]$verifyBeforePatch.ok
      status = [string]$verifyBeforePatch.status
    }
    verify_after = @{
      ok = [bool]$verifyAfterPatch.ok
      status = [string]$verifyAfterPatch.status
    }
    patch_id = $patchId
  }
}

$identity = Get-Content -LiteralPath (Join-Path $root "config\app_identity.json") -Raw | ConvertFrom-Json
$script:appName = $identity.display_name
$releaseName = "$appName-$($identity.version)-$(Get-Slug $identity.channel)"
$releaseDir = Join-Path $root "releases\$releaseName"
$installerPath = Join-Path $releaseDir "$releaseName-setup.exe"
$evidencePath = Join-Path $releaseDir "installed_app_smoke.json"

if (-not $SkipBuild) {
  & (Join-Path $root "scripts\build_installer.ps1") -AllowDirty:$AllowDirty
  if ($LASTEXITCODE -ne 0) {
    throw "Installer build failed with exit code $LASTEXITCODE"
  }
}

if (-not (Test-Path -LiteralPath $installerPath)) {
  throw "Installer was not found: $installerPath"
}

$smokeRoot = Join-Path ([System.IO.Path]::GetTempPath()) "TalosInstalledAppSmoke"
$installDir = Join-Path $smokeRoot $appName
$appDataDir = Join-Path $smokeRoot "app-data"
$installedExe = Join-Path $installDir "$appName.exe"
$uninstaller = Join-Path $installDir "unins000.exe"
$oldAppData = $env:TALOS_APP_DATA_DIR
$oldSmokeHarness = $env:TALOS_SMOKE_HARNESS
$appProcess = $null
$healthResult = $null
$autoHarnessResult = $null

if (Test-Path -LiteralPath $installDir) {
  $oldUninstaller = Join-Path $installDir "unins000.exe"
  if (Test-Path -LiteralPath $oldUninstaller) {
    Invoke-ProcessChecked $oldUninstaller @("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART") "Previous uninstall"
  }
  if (Test-Path -LiteralPath $installDir) {
    Remove-Item -LiteralPath $installDir -Recurse -Force
  }
}
if (Test-Path -LiteralPath $appDataDir) {
  Remove-Item -LiteralPath $appDataDir -Recurse -Force
}

New-Item -ItemType Directory -Path $smokeRoot -Force | Out-Null
Invoke-ProcessChecked $installerPath @(
  "/VERYSILENT",
  "/SUPPRESSMSGBOXES",
  "/NORESTART",
  "/DIR=$installDir"
) "Silent install"

if (-not (Test-Path -LiteralPath $installedExe)) {
  throw "Installed executable was not found: $installedExe"
}
if (Test-Path -LiteralPath (Join-Path $installDir "config\config.json")) {
  throw "Installed app contains writable config in the install directory."
}

try {
  if (-not $SkipLaunch) {
    $env:TALOS_APP_DATA_DIR = $appDataDir
    if ($AutoArduinoHarness) {
      $env:TALOS_SMOKE_HARNESS = "1"
    }
    $appProcess = Start-Process -FilePath $installedExe -WorkingDirectory $installDir -PassThru
    $healthResult = Wait-TalosHealth $TimeoutSec
    $build = $healthResult.health.build
    if ($build.mode -ne "packaged") {
      throw "Installed app did not report packaged mode."
    }
    if (-not [string]::IsNullOrWhiteSpace([string]$build.root) -and [string]$build.root -like "$root*") {
      throw "Installed app build root points back to the source checkout."
    }
    if ($AutoArduinoHarness) {
      $autoHarnessResult = Invoke-AutoArduinoHarness $healthResult.port $smokeRoot
    }
  }

  $manualSteps = @(
    "launch-installed-talos",
    "detect-open-arduino-sketch",
    "select-sketch-and-board",
    "open-source-file",
    "edit-in-talos-and-save-file",
    "verify-sandbox",
    "ask-codex-for-safe-change",
    "review-apply-and-save-codex-change",
    "verify-sandbox-again",
    "confirm-arduino-ide-reflects-saved-change"
  )
  $autoConfirmed = $autoHarnessResult -and [bool]$autoHarnessResult.confirmed
  $status = if (($ManualArduinoConfirmed -or $autoConfirmed) -and (-not $SkipLaunch)) { "passed" } elseif ($ManualArduinoConfirmed) { "manual-confirmed-without-launch-check" } else { "manual-confirmation-required" }
  $evidence = @{
    schema_version = 1
    test = "installed-app-arduino-codex-smoke"
    status = $status
    checked_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss zzz")
    release = $releaseName
    installer = $installerPath
    install_dir = $installDir
    app_data_dir = $appDataDir
    automated = @{
      installed_executable = (Test-Path -LiteralPath $installedExe)
      install_dir_config_absent = -not (Test-Path -LiteralPath (Join-Path $installDir "config\config.json"))
      launched = -not $SkipLaunch
      health_port = if ($healthResult) { $healthResult.port } else { $null }
      packaged_mode = if ($healthResult) { $healthResult.health.build.mode -eq "packaged" } else { $false }
      arduino_codex_harness = if ($autoHarnessResult) { $autoHarnessResult } else { $null }
    }
    manual = @{
      confirmed = [bool]$ManualArduinoConfirmed
      required_steps = $manualSteps
    }
  }
  Write-SmokeEvidence $evidencePath $evidence

  if (-not $ManualArduinoConfirmed -and -not $autoConfirmed) {
    Write-Warning "Automated installed-app smoke completed, but Arduino/Codex manual confirmation is still required."
    Write-Host "Manual checklist: docs\INSTALLED_APP_SMOKE_TEST.md"
  }
  Write-Host "Installed app smoke evidence:"
  Write-Host $evidencePath
} finally {
  Stop-InstalledTalos $appProcess $installDir
  $env:TALOS_APP_DATA_DIR = $oldAppData
  $env:TALOS_SMOKE_HARNESS = $oldSmokeHarness
  if (-not $KeepInstalled) {
    if (Test-Path -LiteralPath $uninstaller) {
      Invoke-ProcessChecked $uninstaller @("/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART") "Smoke uninstall"
    }
    if (Test-Path -LiteralPath $installDir) {
      Remove-TreeWithRetry $installDir
    }
    if (Test-Path -LiteralPath $appDataDir) {
      Remove-TreeWithRetry $appDataDir
    }
  }
}
