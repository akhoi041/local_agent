param(
    [string]$OutDir = "bin"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $root "talos_native.c"
$outputDir = Join-Path $root $OutDir
$output = Join-Path $outputDir "talos_native.dll"

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

function Invoke-Compiler {
    param(
        [string]$Compiler,
        [string[]]$CompilerArgs
    )
    & $Compiler @CompilerArgs
    if ($LASTEXITCODE -ne 0) {
        throw "$Compiler failed with exit code $LASTEXITCODE"
    }
}

$gcc = Get-Command gcc -ErrorAction SilentlyContinue
if ($gcc) {
    Invoke-Compiler -Compiler $gcc.Source -CompilerArgs @(
        "-shared",
        "-O2",
        "-municode",
        "-Wall",
        "-Wextra",
        "-o", $output,
        $source,
        "-luser32"
    )
    Write-Host "Built $output"
    exit 0
}

$clang = Get-Command clang -ErrorAction SilentlyContinue
if (-not $clang) {
    $clangPath = "C:\Program Files\LLVM\bin\clang.exe"
    if (Test-Path -LiteralPath $clangPath) {
        $clang = [pscustomobject]@{ Source = $clangPath }
    }
}
if ($clang) {
    Invoke-Compiler -Compiler $clang.Source -CompilerArgs @(
        "-shared",
        "-O2",
        "-Wall",
        "-Wextra",
        "-o", $output,
        $source,
        "-luser32"
    )
    Write-Host "Built $output"
    exit 0
}

$cl = Get-Command cl -ErrorAction SilentlyContinue
if ($cl) {
    Invoke-Compiler -Compiler $cl.Source -CompilerArgs @(
        "/LD",
        "/O2",
        "/W3",
        "/Fe:$output",
        $source,
        "user32.lib"
    )
    Write-Host "Built $output"
    exit 0
}

throw "No C compiler found. Install MinGW-w64, LLVM clang, or Visual Studio Build Tools, then rerun native/build.ps1."
