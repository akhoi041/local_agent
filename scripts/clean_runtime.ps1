param(
    [switch]$KeepStaging
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$appDataRoot = if ($env:TALOS_APP_DATA_DIR) {
    [System.IO.Path]::GetFullPath($env:TALOS_APP_DATA_DIR)
} else {
    $localAppData = if ($env:LOCALAPPDATA) { $env:LOCALAPPDATA } else { Join-Path $HOME "AppData\Local" }
    [System.IO.Path]::GetFullPath((Join-Path $localAppData "T-Engine\Talos"))
}
$targets = @()

function Add-TargetIfExists([string]$PathText) {
    if (Test-Path -LiteralPath $PathText) {
        $script:targets += $PathText
    }
}

Add-TargetIfExists (Join-Path $root ".talos_sandbox")
Add-TargetIfExists (Join-Path $appDataRoot "sandbox")
if (-not $KeepStaging) {
    Add-TargetIfExists (Join-Path $root ".talos_staging")
    Add-TargetIfExists (Join-Path $appDataRoot "staging")
}
$targets += Get-ChildItem -LiteralPath $root -Directory -Force -Filter "pytest-cache-files-*" |
    ForEach-Object { $_.FullName }
$targets += Get-ChildItem -LiteralPath $root -Directory -Force -Recurse -Filter "__pycache__" |
    ForEach-Object { $_.FullName }

foreach ($candidate in $targets | Select-Object -Unique) {
    $target = Resolve-Path -LiteralPath $candidate -ErrorAction SilentlyContinue
    if ($null -eq $target) {
        continue
    }
    $insideWorkspace = $target.Path.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)
    $insideAppData = $target.Path.StartsWith($appDataRoot, [System.StringComparison]::OrdinalIgnoreCase)
    if (-not $insideWorkspace -and -not $insideAppData) {
        throw "Refusing to remove a path outside the Talos workspace or app data root: $($target.Path)"
    }
    try {
        Remove-Item -LiteralPath $target.Path -Recurse -Force
        Write-Host "Removed $($target.Path)"
    } catch {
        Write-Warning "Could not remove $($target.Path) because it is in use or protected: $($_.Exception.Message)"
    }
}
