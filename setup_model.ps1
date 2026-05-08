$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
  Write-Host "Ollama is not installed or not in PATH."
  Write-Host "Install Ollama first, then run this script again."
  exit 1
}

$model = "qwen2.5:7b-instruct-q3_K_L"
ollama pull $model

$configPath = Join-Path $root "config.json"
$config = Get-Content $configPath -Raw | ConvertFrom-Json
$config.model = $model
$config.model_enabled = $true
$config | ConvertTo-Json -Depth 8 | Set-Content $configPath -Encoding UTF8

Write-Host "Model is ready: $model"
