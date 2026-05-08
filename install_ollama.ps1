$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$installer = Join-Path $root "OllamaSetup.exe"

try {
  Invoke-WebRequest -Uri "https://ollama.com/download/OllamaSetup.exe" -OutFile $installer -ErrorAction Stop
} catch {
  Write-Host "Could not download OllamaSetup.exe from the official Ollama endpoint."
  Write-Host "The download currently depends on release-assets.githubusercontent.com."
  Write-Host "Error: $($_.Exception.Message)"
  Write-Host ""
  Write-Host "Manual fallback:"
  Write-Host "1. Open https://ollama.com/download/windows"
  Write-Host "2. Download and run OllamaSetup.exe"
  Write-Host "3. Reopen PowerShell and run .\setup_model.ps1"
  exit 1
}

Start-Process -FilePath $installer -Wait
& (Join-Path $root "setup_model.ps1")
