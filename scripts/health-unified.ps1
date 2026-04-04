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

$envFile = Join-Path $RootPath ".env"
Load-EnvFile -EnvPath $envFile

$runtimeDir = Join-Path $RootPath ".runtime"
$frontendPid = Join-Path $runtimeDir "frontend.pid"
$backendPid = Join-Path $runtimeDir "backend.pid"

function Read-Pid {
    param([string]$PidFile)
    if (-not (Test-Path $PidFile)) { return $null }
    $processIdText = (Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1).Trim()
    if (-not $processIdText) { return $null }
    return [int]$processIdText
}

function Test-ProcessRunning {
    param([int]$ProcessId)
    if (-not $ProcessId) { return $false }
    return $null -ne (Get-Process -Id $ProcessId -ErrorAction SilentlyContinue)
}

$frontendUrl = $env:SMART_MIRROR_FRONTEND_URL
if (-not $frontendUrl) {
    $frontendUrl = "http://localhost:8080"
}

$frontendPidValue = Read-Pid -PidFile $frontendPid
$backendPidValue = Read-Pid -PidFile $backendPid

$frontendRunning = Test-ProcessRunning -ProcessId $frontendPidValue
$backendRunning = Test-ProcessRunning -ProcessId $backendPidValue

$frontendHttp = $false
try {
    $versionUrl = "$frontendUrl/version"
    $resp = Invoke-WebRequest -Uri $versionUrl -UseBasicParsing -TimeoutSec 3
    if ($resp.StatusCode -eq 200) {
        $frontendHttp = $true
    }
} catch {
    $frontendHttp = $false
}

Write-Host "frontend_process: $frontendRunning (pid=$frontendPidValue)"
Write-Host "backend_process : $backendRunning (pid=$backendPidValue)"
Write-Host "frontend_http   : $frontendHttp ($frontendUrl/version)"

if ($frontendHttp -and $backendRunning) {
    exit 0
}

exit 1
