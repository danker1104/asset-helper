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

Write-Host '하나의 창에서 백엔드와 프론트엔드를 동시에 실행합니다.' -ForegroundColor Cyan
Write-Host '종료하려면 Ctrl+C를 누르세요.' -ForegroundColor Yellow
Write-Host 'API: http://127.0.0.1:8000 (docs: /docs)' -ForegroundColor Green
Write-Host 'Web: http://127.0.0.1:3100' -ForegroundColor Green

$apiJob = $null
$webJob = $null
$openedWeb = $false
$openedApiDocs = $false

function Stop-ProcessesByPort {
    param(
        [int]$Port
    )

    $pids = @()

    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        if ($null -ne $connections) {
            $pids += ($connections | Select-Object -ExpandProperty OwningProcess -Unique)
        }
    }
    catch {
    }

    if ($pids.Count -eq 0) {
        try {
            $lines = netstat -ano -p tcp | Select-String ":$Port"
            foreach ($line in $lines) {
                $parts = ($line.ToString() -replace '^\s+', '') -split '\s+'
                if ($parts.Length -ge 5) {
                    $pidFromNetstat = 0
                    if ([int]::TryParse($parts[4], [ref]$pidFromNetstat)) {
                        $pids += $pidFromNetstat
                    }
                }
            }
        }
        catch {
        }
    }

    $pids = $pids | Sort-Object -Unique
    foreach ($processId in $pids) {
        if ($processId -and $processId -ne $PID) {
            try {
                Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                Write-Host "포트 $Port 점유 프로세스 종료: PID $processId" -ForegroundColor DarkYellow
            }
            catch {
            }
        }
    }
}

try {
    Stop-ProcessesByPort -Port 8000
    Stop-ProcessesByPort -Port 3100

    $apiJob = Start-Job -Name 'asset-helper-api' -ArgumentList $apiPath, $python -ScriptBlock {
        param($workDir, $pythonExe)
        Set-Location $workDir
        & $pythonExe -m uvicorn asset_helper.main:create_app --factory --reload --app-dir src --env-file .env 2>&1 |
            ForEach-Object { "[api] $_" }
    }

    $webJob = Start-Job -Name 'asset-helper-web' -ArgumentList $webPath -ScriptBlock {
        param($workDir)
        Set-Location $workDir
        & npm.cmd run dev -- --port 3100 --hostname 127.0.0.1 2>&1 |
            ForEach-Object { "[web] $_" }
    }

    while ($true) {
        if ($apiJob.State -in @('Failed', 'Stopped', 'Completed')) {
            Receive-Job -Job $apiJob -Keep | Write-Host
            if ($webJob.State -notin @('Failed', 'Stopped', 'Completed')) {
                Stop-Job -Job $webJob -ErrorAction SilentlyContinue
            }
            break
        }

        if ($webJob.State -in @('Failed', 'Stopped', 'Completed')) {
            Receive-Job -Job $webJob -Keep | Write-Host
            if ($apiJob.State -notin @('Failed', 'Stopped', 'Completed')) {
                Stop-Job -Job $apiJob -ErrorAction SilentlyContinue
            }
            break
        }

        Receive-Job -Job $apiJob | Write-Host
        Receive-Job -Job $webJob | Write-Host

        if (-not $openedWeb) {
            try {
                $response = Invoke-WebRequest -Uri 'http://127.0.0.1:3100' -Method Get -TimeoutSec 1
                if ($response.StatusCode -ge 200) {
                    Start-Process 'http://127.0.0.1:3100' | Out-Null
                    $openedWeb = $true
                }
            }
            catch {
            }
        }

        if (-not $openedApiDocs) {
            try {
                $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -Method Get -TimeoutSec 1
                if ($response.StatusCode -eq 200) {
                    Start-Process 'http://127.0.0.1:8000/docs' | Out-Null
                    $openedApiDocs = $true
                }
            }
            catch {
            }
        }

        Wait-Job -Job @($apiJob, $webJob) -Any -Timeout 1 | Out-Null
    }
}
finally {
    foreach ($job in @($apiJob, $webJob)) {
        if ($null -ne $job) {
            try {
                Stop-Job -Job $job -ErrorAction SilentlyContinue
            }
            catch {
            }
            try {
                Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
            }
            catch {
            }
        }
    }
}
