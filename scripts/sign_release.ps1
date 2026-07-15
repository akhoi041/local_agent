param(
  [string]$ReleaseDir = "",
  [string]$CertificateThumbprint = "",
  [string]$CertificateSubject = "",
  [switch]$AllowUnsignedBeta
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
Set-Location $root
$ErrorActionPreference = "Stop"

function Get-Slug([string]$value) {
  return ($value.Trim().ToLowerInvariant() -replace '[^a-z0-9]+', '-').Trim('-')
}

function Resolve-ReleaseDir {
  param([string]$Candidate)
  if ($Candidate) {
    if ([System.IO.Path]::IsPathRooted($Candidate)) {
      return [System.IO.Path]::GetFullPath($Candidate)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $root $Candidate))
  }
  $identity = Get-Content -LiteralPath (Join-Path $root "config\app_identity.json") -Raw | ConvertFrom-Json
  $releaseName = "$($identity.display_name)-$($identity.version)-$(Get-Slug $identity.channel)"
  return Join-Path $root "releases\$releaseName"
}

function Find-SignTool {
  $command = Get-Command signtool.exe -ErrorAction SilentlyContinue
  if ($command) {
    return $command.Source
  }
  $kitRoot = "${env:ProgramFiles(x86)}\Windows Kits\10\bin"
  if (Test-Path -LiteralPath $kitRoot) {
    $candidate = Get-ChildItem -LiteralPath $kitRoot -Recurse -Filter signtool.exe -File -ErrorAction SilentlyContinue |
      Sort-Object FullName -Descending |
      Select-Object -First 1
    if ($candidate) {
      return $candidate.FullName
    }
  }
  throw "signtool.exe was not found. Install the Windows SDK or add signtool.exe to PATH."
}

function Get-ArtifactStatus {
  param([System.IO.FileInfo]$File)
  $hash = Get-FileHash -LiteralPath $File.FullName -Algorithm SHA256
  $signature = Get-AuthenticodeSignature -LiteralPath $File.FullName
  return [ordered]@{
    file = $File.Name
    sha256 = $hash.Hash
    bytes = $File.Length
    authenticode_status = [string]$signature.Status
    signer = if ($signature.SignerCertificate) { $signature.SignerCertificate.Subject } else { "" }
  }
}

function Write-SigningStatus {
  param(
    [string]$Path,
    [string]$Status,
    [bool]$Signed,
    [string]$Reason,
    [object[]]$Artifacts,
    [object]$Policy
  )
  $payload = [ordered]@{
    schema_version = 1
    status = $Status
    signed = $Signed
    reason = $Reason
    policy_status = [string]$Policy.status
    digest_algorithm = [string]$Policy.digest_algorithm
    timestamp_server = [string]$Policy.timestamp_server
    checked_at = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss zzz")
    artifacts = $Artifacts
  }
  $payload | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $Path -Encoding utf8
}

$policyPath = Join-Path $root "config\signing_policy.json"
if (-not (Test-Path -LiteralPath $policyPath)) {
  throw "Signing policy was not found: $policyPath"
}
$policy = Get-Content -LiteralPath $policyPath -Raw | ConvertFrom-Json
$resolvedReleaseDir = Resolve-ReleaseDir $ReleaseDir
if (-not (Test-Path -LiteralPath $resolvedReleaseDir)) {
  throw "Release directory was not found: $resolvedReleaseDir"
}

$artifacts = @(Get-ChildItem -LiteralPath $resolvedReleaseDir -Filter "*.exe" -File | Sort-Object Name)
if (-not $artifacts) {
  throw "No .exe artifacts were found in release directory: $resolvedReleaseDir"
}

$statusPath = Join-Path $resolvedReleaseDir "signing_status.json"

if (-not $CertificateThumbprint -and -not $CertificateSubject) {
  if (-not $AllowUnsignedBeta -or -not [bool]$policy.unsigned_beta_allowed) {
    throw "No signing certificate was provided. Use -CertificateThumbprint, -CertificateSubject, or explicitly pass -AllowUnsignedBeta for the Pre-Alpha/Beta channel."
  }
  $artifactStatus = @($artifacts | ForEach-Object { Get-ArtifactStatus $_ })
  Write-SigningStatus `
    -Path $statusPath `
    -Status "unsigned-beta" `
    -Signed $false `
    -Reason "Unsigned Pre-Alpha/Beta was explicitly allowed for this release." `
    -Artifacts $artifactStatus `
    -Policy $policy
  Write-Warning "Release recorded as unsigned Pre-Alpha/Beta: $statusPath"
  return
}

$signTool = Find-SignTool
foreach ($artifact in $artifacts) {
  $args = @(
    "sign",
    "/fd", [string]$policy.digest_algorithm,
    "/td", [string]$policy.digest_algorithm,
    "/tr", [string]$policy.timestamp_server
  )
  if ($CertificateThumbprint) {
    $args += @("/sha1", $CertificateThumbprint)
  } else {
    $args += @("/n", $CertificateSubject)
  }
  $args += $artifact.FullName
  & $signTool @args
  if ($LASTEXITCODE -ne 0) {
    throw "signtool failed for $($artifact.Name) with exit code $LASTEXITCODE"
  }
}

$artifactStatus = @($artifacts | ForEach-Object { Get-ArtifactStatus $_ })
$notSigned = @($artifactStatus | Where-Object { $_.authenticode_status -ne "Valid" })
if ($notSigned) {
  Write-SigningStatus `
    -Path $statusPath `
    -Status "signing-verification-failed" `
    -Signed $false `
    -Reason "One or more artifacts did not verify as Valid after signing." `
    -Artifacts $artifactStatus `
    -Policy $policy
  throw "Signing verification failed. See $statusPath"
}

Write-SigningStatus `
  -Path $statusPath `
  -Status "signed" `
  -Signed $true `
  -Reason "All release artifacts verified with Authenticode." `
  -Artifacts $artifactStatus `
  -Policy $policy
Write-Host "Release signing status:"
Write-Host $statusPath
