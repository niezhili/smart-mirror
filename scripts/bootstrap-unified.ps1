param(
    [string]$RootPath = (Resolve-Path (Join-Path $PSScriptRoot ".."))
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

if (-not $env:SMART_MIRROR_PYTHON_EXE) {
    if ($env:CONDA_PREFIX -and (Test-Path (Join-Path $env:CONDA_PREFIX "python.exe"))) {
        $env:SMART_MIRROR_PYTHON_EXE = (Join-Path $env:CONDA_PREFIX "python.exe")
    } else {
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($null -eq $pythonCmd) {
            throw "python command not found. Please activate your Python environment first."
        }
        $env:SMART_MIRROR_PYTHON_EXE = $pythonCmd.Source
    }
}

$frontendPath = Join-Path $RootPath "smart-mirror-frontend"
if (-not (Test-Path $frontendPath)) {
    $frontendPath = Join-Path $RootPath "smart-mirror-js"
}

$backendPath = Join-Path $RootPath "smart-mirror-backend"
if (-not (Test-Path $backendPath)) {
    $backendPath = Join-Path $RootPath "smart-mirror-main"
}

$pythonExe = $env:SMART_MIRROR_PYTHON_EXE

Write-Host "Installing frontend dependencies..."
Push-Location $frontendPath
if ($IsWindows) {
    npm install --ignore-scripts
} else {
    npm install
}
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    throw "frontend dependency installation failed"
}
Pop-Location

Write-Host "Installing backend dependencies..."
Push-Location $backendPath
& $pythonExe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    throw "backend dependency installation failed"
}
Pop-Location

Write-Host "Bootstrap completed."
