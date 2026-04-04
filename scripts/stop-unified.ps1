param(
    [string]$RootPath = (Resolve-Path (Join-Path $PSScriptRoot ".."))
)

$ErrorActionPreference = "Continue"

function Load-EnvFile {
    param([string]$EnvPath)

    if (-not (Test-Path $EnvPath)) {
        return
    }

    Get-Content $EnvPath | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith("#")) {
            return
        }

        $idx = $line.IndexOf("=")
        if ($idx -lt 1) {
            return
        }

        $key = $line.Substring(0, $idx).Trim()
        $value = $line.Substring($idx + 1).Trim().Trim('"')
        [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}

$runtimeDir = Join-Path $RootPath ".runtime"
$frontendPid = Join-Path $runtimeDir "frontend.pid"
$backendPid = Join-Path $runtimeDir "backend.pid"

$envFile = Join-Path $RootPath ".env"
Load-EnvFile -EnvPath $envFile

function Stop-ByPidFile {
    param(
        [string]$PidFile,
        [string]$Name
    )

    if (-not (Test-Path $PidFile)) {
        Write-Host "$Name pid file not found, skip."
        return
    }

    $processIdText = (Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
    if (-not $processIdText) {
        Write-Host "$Name pid file is empty, skip."
        return
    }

    $processId = [int]$processIdText
    $proc = Get-Process -Id $processId -ErrorAction SilentlyContinue
    if ($null -ne $proc) {
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        Write-Host "Stopped $Name process: $processId"
    } else {
        Write-Host "$Name process not running: $processId"
    }

    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

Stop-ByPidFile -PidFile $frontendPid -Name "frontend"
Stop-ByPidFile -PidFile $backendPid -Name "backend"

$frontendPort = $env:SMART_MIRROR_FRONTEND_PORT
if (-not $frontendPort) {
    $frontendPort = "8080"
}

try {
    $connections = Get-NetTCPConnection -LocalPort ([int]$frontendPort) -State Listen -ErrorAction SilentlyContinue
    if ($connections) {
        $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($pidValue in $pids) {
            if ($pidValue -and $pidValue -ne $PID) {
                Stop-Process -Id $pidValue -Force -ErrorAction SilentlyContinue
                Write-Host "Stopped frontend listener on port ${frontendPort}: $pidValue"
            }
        }
    }
} catch {
}
