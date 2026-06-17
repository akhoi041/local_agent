$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $scriptDir
$src = Join-Path $root "native\talos_native.c"
$outDir = Join-Path $root "native\bin"
$dll = Join-Path $outDir "talos_native.dll"

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Path $outDir -Force | Out-Null

$cl = Get-Command cl.exe -ErrorAction SilentlyContinue
if ($cl) {
  & $cl.Source /nologo /LD /O2 /W3 /Fe:$dll $src user32.lib kernel32.lib
  if ($LASTEXITCODE -ne 0) { throw "cl.exe failed with exit code $LASTEXITCODE" }
  Write-Host "Built native library:"
  Write-Host $dll
  exit 0
}

$gcc = Get-Command gcc.exe -ErrorAction SilentlyContinue
if (-not $gcc) {
  $wingetPackages = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Packages"
  if (Test-Path -LiteralPath $wingetPackages) {
    $gcc = Get-ChildItem -LiteralPath $wingetPackages -Recurse -Filter gcc.exe -ErrorAction SilentlyContinue |
      Where-Object { $_.FullName -match '\\mingw64\\bin\\gcc\.exe$' } |
      Select-Object -First 1
  }
}
if ($gcc) {
  $gccPath = if ($gcc.Source) { $gcc.Source } else { $gcc.FullName }
  & $gccPath -shared -O2 -municode -o $dll $src -luser32 -lkernel32
  if ($LASTEXITCODE -ne 0) { throw "gcc.exe failed with exit code $LASTEXITCODE" }
  Write-Host "Built native library:"
  Write-Host $dll
  exit 0
}

throw "No C compiler found. Install Visual Studio Build Tools or MinGW-w64, then run .\scripts\build_native.ps1 again."
