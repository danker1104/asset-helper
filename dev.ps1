$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiPath = Join-Path $root 'apps/api'
$webPath = Join-Path $root 'apps/web'
$venvPython = Join-Path $root '.venv/Scripts/python.exe'
$systemPython = 'C:/Users/seang/AppData/Local/Programs/Python/Python312/python.exe'
$python = if (Test-Path $venvPython) { $venvPython } else { $systemPython }

if (-not (Test-Path $apiPath)) {
	throw "API path not found: $apiPath"
}

if (-not (Test-Path $webPath)) {
	throw "Web path not found: $webPath"
}

if (-not (Test-Path $python)) {
	throw "Python executable not found: $python"
}

$apiCommand = "Set-Location '$apiPath'; & '$python' -m uvicorn asset_helper.main:create_app --factory --reload --app-dir src"
$webCommand = "Set-Location '$webPath'; npm.cmd run dev -- --port 3100 --hostname 127.0.0.1"

Start-Process pwsh -ArgumentList @('-NoExit', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', $apiCommand) | Out-Null
Start-Process pwsh -ArgumentList @('-NoExit', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', $webCommand) | Out-Null

Write-Host 'API/WEB 서버를 각각 새 창에서 동시에 시작했습니다.' -ForegroundColor Green
Write-Host 'API: http://127.0.0.1:8000' -ForegroundColor Cyan
Write-Host 'WEB: http://127.0.0.1:3100' -ForegroundColor Cyan
