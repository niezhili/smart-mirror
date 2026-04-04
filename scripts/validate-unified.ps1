param(
    [string]$RootPath = (Resolve-Path (Join-Path $PSScriptRoot "..")),
    [switch]$SkipDependencyCheck
)

$ErrorActionPreference = "Stop"

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

$frontendPath = Join-Path $RootPath "smart-mirror-frontend"
if (-not (Test-Path $frontendPath)) {
    $frontendPath = Join-Path $RootPath "smart-mirror-js"
}

$backendPath = Join-Path $RootPath "smart-mirror-backend"
if (-not (Test-Path $backendPath)) {
    $backendPath = Join-Path $RootPath "smart-mirror-main"
}

if (-not (Test-Path $frontendPath)) {
    throw "Missing folder: $frontendPath"
}
if (-not (Test-Path $backendPath)) {
    throw "Missing folder: $backendPath"
}
if (-not (Test-Path (Join-Path $frontendPath "package.json"))) {
    throw "Missing frontend package.json"
}
if (-not (Test-Path (Join-Path $backendPath "main.py"))) {
    throw "Missing backend main.py"
}

if (-not $env:SMART_MIRROR_FRONTEND_URL) {
    $env:SMART_MIRROR_FRONTEND_URL = "http://localhost:8080"
}
if (-not $env:SMART_MIRROR_FRONTEND_MODE) {
    $env:SMART_MIRROR_FRONTEND_MODE = "server"
}
if (-not $env:SMART_MIRROR_ENABLE_BACKEND_GUI) {
    $env:SMART_MIRROR_ENABLE_BACKEND_GUI = "false"
}

if (-not $env:SMART_MIRROR_PYTHON_EXE) {
    if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) {
        $env:SMART_MIRROR_PYTHON_EXE = (Join-Path $env:CONDA_PREFIX "python.exe")
    } else {
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($null -eq $pythonCmd) {
            throw "python command not found. Activate Python env first."
        }
        $env:SMART_MIRROR_PYTHON_EXE = $pythonCmd.Source
    }
}

$pythonExe = $env:SMART_MIRROR_PYTHON_EXE
if (-not (Test-Path $pythonExe)) {
    throw "SMART_MIRROR_PYTHON_EXE not found: $pythonExe"
}

if (-not $SkipDependencyCheck) {
    $missing = @()

    if (-not (Test-Path (Join-Path $frontendPath "node_modules"))) {
        $missing += "frontend node_modules"
    }

    $frontendModuleAlias = Join-Path $frontendPath "node_modules\module-alias\register.js"
    if (-not (Test-Path $frontendModuleAlias)) {
        $missing += "frontend module-alias"
    }

    Push-Location $backendPath
    & $pythonExe -c "import geocoder" 2>$null
    if ($LASTEXITCODE -ne 0) {
        $missing += "backend geocoder"
    }
    Pop-Location

    if ($missing.Count -gt 0) {
        Write-Host "Missing dependencies detected:" -ForegroundColor Yellow
        $missing | ForEach-Object { Write-Host "- $_" -ForegroundColor Yellow }
        Write-Host "Run: powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\bootstrap-unified.ps1" -ForegroundColor Cyan
        exit 1
    }
}

Write-Host "Unified validation passed."
Write-Host "Frontend mode: $($env:SMART_MIRROR_FRONTEND_MODE)"
Write-Host "Frontend URL : $($env:SMART_MIRROR_FRONTEND_URL)"
Write-Host "Python exe   : $pythonExe"
