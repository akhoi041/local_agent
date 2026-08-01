param(
    [switch]$Manifest
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$manifestPath = Join-Path $repoRoot "core\talos_core\Cargo.toml"
$cargoCommand = Get-Command cargo -ErrorAction SilentlyContinue

if ($cargoCommand) {
    $cargo = $cargoCommand.Source
} else {
    $cargo = Join-Path $env:USERPROFILE ".cargo\bin\cargo.exe"
    if (-not (Test-Path -LiteralPath $cargo)) {
        throw "cargo was not found. Run Stage 0 toolchain setup before this check."
    }
}

& $cargo test --manifest-path $manifestPath
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$mode = if ($Manifest) { "manifest" } else { "summary" }
& $cargo run --quiet --manifest-path $manifestPath -- $mode
exit $LASTEXITCODE
