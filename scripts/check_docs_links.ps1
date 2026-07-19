param(
  [string]$Root
)

$ErrorActionPreference = "Stop"

if (-not $Root) {
  $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
  $Root = Split-Path -Parent $scriptDir
}

$rootPath = (Resolve-Path -LiteralPath $Root).Path
$missing = New-Object System.Collections.Generic.List[string]
$checked = New-Object System.Collections.Generic.HashSet[string]

function Normalize-RepoPath([string]$value) {
  $path = $value.Trim().Trim("`"", "'", ")", "]", "}", ".", ",", ";", ":")
  $path = $path -replace '\\', '/'
  while ($path.StartsWith("../")) {
    $path = $path.Substring(3)
  }
  return $path
}

function Test-RepoPath([string]$repoPath) {
  $normalized = Normalize-RepoPath $repoPath
  if (-not $normalized) {
    return
  }
  if (-not ($normalized.StartsWith("docs/") -or $normalized.StartsWith("dev_notes/"))) {
    return
  }
  $leaf = Split-Path -Leaf $normalized
  $extension = [System.IO.Path]::GetExtension($leaf)
  if (-not $extension -and $leaf -ne "LICENSE") {
    return
  }
  if ($checked.Contains($normalized)) {
    return
  }
  $checked.Add($normalized) | Out-Null
  $fullPath = Join-Path $rootPath ($normalized -replace '/', [System.IO.Path]::DirectorySeparatorChar)
  if (-not (Test-Path -LiteralPath $fullPath)) {
    $missing.Add($normalized) | Out-Null
  }
}

$requiredPaths = @(
  "docs/README.md",
  "docs/DOCS_INDEX.md",
  "docs/LICENSE",
  "docs/EULA.md",
  "docs/PRIVACY.md",
  "docs/THIRD_PARTY_NOTICES.md",
  "docs/CODE_SIGNING.md",
  "docs/DISTRIBUTION_COPY.md",
  "docs/RELEASE_NOTES.md",
  "docs/TALOS_USER_GUIDE.md",
  "docs/TALOS_FIRST_RUN_CHECKLIST.md",
  "docs/TALOS_TROUBLESHOOTING.md",
  "docs/TALOS_RECOVERY_GUIDE.md",
  "docs/TALOS_SUPPORT_DEBUG.md",
  "docs/TALOS_DIAGNOSTICS.md",
  "docs/TALOS_INSTALL_LIFECYCLE.md",
  "docs/ARDUINO_SMOKE_TEST.md",
  "docs/INSTALLED_APP_SMOKE_TEST.md",
  "docs/TALOS_UI_UX_CHECKLIST.md",
  "dev_notes/README.md",
  "dev_notes/roadmap/TALOS_ROADMAP.md",
  "dev_notes/pipelines/TALOS_PIPELINE_010.md",
  "dev_notes/pipelines/TALOS_PIPELINE_020.md",
  "dev_notes/pipelines/TALOS_PIPELINE_030.md",
  "dev_notes/pipelines/TALOS_PIPELINE_040.md",
  "dev_notes/pipelines/TALOS_PIPELINE_050.md",
  "dev_notes/pipelines/TALOS_PIPELINE_055.md",
  "dev_notes/evidence/TALOS_020_EVIDENCE.md",
  "dev_notes/evidence/TALOS_030_EVIDENCE.md",
  "dev_notes/evidence/TALOS_040_EVIDENCE.md",
  "dev_notes/evidence/TALOS_050_EVIDENCE.md",
  "dev_notes/evidence/TALOS_055_EVIDENCE.md"
)

foreach ($path in $requiredPaths) {
  Test-RepoPath $path
}

$scanRoots = @(
  "docs",
  "scripts",
  "installer",
  "ui/web_frontend",
  "tests"
)

$scanFiles = New-Object System.Collections.Generic.List[string]
foreach ($scanRoot in $scanRoots) {
  $fullRoot = Join-Path $rootPath ($scanRoot -replace '/', [System.IO.Path]::DirectorySeparatorChar)
  if (-not (Test-Path -LiteralPath $fullRoot)) {
    continue
  }
  Get-ChildItem -LiteralPath $fullRoot -Recurse -File |
    Where-Object { $_.Extension -in @(".md", ".ps1", ".iss", ".html", ".js", ".py", ".json") -or $_.Name -eq "LICENSE" } |
    ForEach-Object { $scanFiles.Add($_.FullName) | Out-Null }
}

$patterns = @(
  '(?:\.\./)?docs[\\/][A-Za-z0-9_.-]+(?:[\\/][A-Za-z0-9_.-]+)*',
  '(?:\.\./)?dev_notes[\\/][A-Za-z0-9_.-]+(?:[\\/][A-Za-z0-9_.-]+)*'
)

foreach ($file in $scanFiles) {
  $content = Get-Content -LiteralPath $file -Raw
  foreach ($pattern in $patterns) {
    foreach ($match in [regex]::Matches($content, $pattern)) {
      Test-RepoPath $match.Value
    }
  }
}

foreach ($devNote in @(
  "dev_notes/README.md",
  "dev_notes/pipelines/TALOS_PIPELINE_055.md",
  "dev_notes/evidence/TALOS_055_EVIDENCE.md"
)) {
  $fullPath = Join-Path $rootPath ($devNote -replace '/', [System.IO.Path]::DirectorySeparatorChar)
  if (Test-Path -LiteralPath $fullPath) {
    $scanFiles.Add($fullPath) | Out-Null
  }
}

if ($missing.Count -gt 0) {
  Write-Host "Documentation link check failed:"
  foreach ($path in ($missing | Sort-Object -Unique)) {
    Write-Host "  missing: $path"
  }
  exit 1
}

Write-Host ("Documentation link check OK: {0} repo doc references verified." -f $checked.Count)
