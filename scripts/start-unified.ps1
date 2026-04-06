<#
.SYNOPSIS
启动统一版 Smart Mirror 的前端与后端服务。

.DESCRIPTION
先执行环境校验，再以后台 PowerShell 进程启动前后端。
运行日志与 PID 文件会写入 .runtime 目录，
便于后续通过配套脚本进行健康检查与停止服务。

.PARAMETER RootPath
项目根目录路径。默认是当前脚本的上级目录。

.EXAMPLE
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-unified.ps1

.EXAMPLE
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-unified.ps1 -RootPath D:\ProjectCode\smart-mirror
#>
param(
    [string]$RootPath = (Resolve-Path (Join-Path $PSScriptRoot ".."))
)

$ErrorActionPreference = "Stop"

$validateScript = Join-Path $PSScriptRoot "validate-unified.ps1"
& $validateScript -RootPath $RootPath
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

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

if (-not $env:SMART_MIRROR_FRONTEND_URL) {
    $env:SMART_MIRROR_FRONTEND_URL = "http://localhost:8080"
}
if (-not $env:SMART_MIRROR_ENABLE_BACKEND_GUI) {
    $env:SMART_MIRROR_ENABLE_BACKEND_GUI = "false"
}
if (-not $env:SMART_MIRROR_FRONTEND_PORT) {
    $env:SMART_MIRROR_FRONTEND_PORT = "8080"
}
if (-not $env:SMART_MIRROR_FRONTEND_MODE) {
    $env:SMART_MIRROR_FRONTEND_MODE = "server"
}
$runtimeDir = Join-Path $RootPath ".runtime"
if (-not (Test-Path $runtimeDir)) {
    New-Item -ItemType Directory -Path $runtimeDir | Out-Null
}

$frontendPath = Join-Path $RootPath "smart-mirror-frontend"
if (-not (Test-Path $frontendPath)) {
    $frontendPath = Join-Path $RootPath "smart-mirror-js"
}

$backendPath = Join-Path $RootPath "smart-mirror-backend"
if (-not (Test-Path $backendPath)) {
    $backendPath = Join-Path $RootPath "smart-mirror-main"
}

if (-not (Test-Path $frontendPath)) {
    throw "Frontend path not found: $frontendPath"
}
if (-not (Test-Path $backendPath)) {
    throw "Backend path not found: $backendPath"
}

$frontendOutLog = Join-Path $runtimeDir "frontend.out.log"
$frontendErrLog = Join-Path $runtimeDir "frontend.err.log"
$backendOutLog = Join-Path $runtimeDir "backend.out.log"
$backendErrLog = Join-Path $runtimeDir "backend.err.log"
$frontendPid = Join-Path $runtimeDir "frontend.pid"
$backendPid = Join-Path $runtimeDir "backend.pid"

$frontendMode = $env:SMART_MIRROR_FRONTEND_MODE.ToLower()
if ($frontendMode -eq "electron") {
    $frontendFilePath = "powershell"
    $frontendArgumentList = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "Set-Location '$frontendPath'; npm run start:windows")
} else {
    $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
    if ($null -eq $nodeCmd) {
        throw "node command not found. Please install Node.js first."
    }
    $frontendFilePath = $nodeCmd.Source
    $frontendArgumentList = @("./serveronly")
}

$pythonExe = $env:SMART_MIRROR_PYTHON_EXE
$backendFilePath = "powershell"
$backendArgumentList = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "Set-Location '$backendPath'; & '$pythonExe' main.py")

if (-not (Test-Path (Join-Path $frontendPath "package.json"))) {
    throw "Frontend package.json not found."
}
if (-not (Test-Path (Join-Path $backendPath "main.py"))) {
    throw "Backend main.py not found."
}

$frontendProc = Start-Process -FilePath $frontendFilePath -ArgumentList $frontendArgumentList -WorkingDirectory $frontendPath -RedirectStandardOutput $frontendOutLog -RedirectStandardError $frontendErrLog -WindowStyle Hidden -PassThru
$backendProc = Start-Process -FilePath $backendFilePath -ArgumentList $backendArgumentList -RedirectStandardOutput $backendOutLog -RedirectStandardError $backendErrLog -WindowStyle Hidden -PassThru

$frontendAlive = $null -ne (Get-Process -Id $frontendProc.Id -ErrorAction SilentlyContinue)
$backendAlive = $null -ne (Get-Process -Id $backendProc.Id -ErrorAction SilentlyContinue)

if (-not $frontendAlive -or -not $backendAlive) {
    Write-Error "Unified startup failed. Check logs: $runtimeDir"
    if (-not $frontendAlive) {
        Write-Error "Frontend exited early. See: $frontendErrLog"
    }
    if (-not $backendAlive) {
        Write-Error "Backend exited early. See: $backendErrLog"
    }
    exit 1
}

$frontendProc.Id | Out-File -FilePath $frontendPid -Encoding ascii -Force
$backendProc.Id | Out-File -FilePath $backendPid -Encoding ascii -Force

Write-Host "Unified startup launched."
Write-Host "Frontend PID: $($frontendProc.Id)"
Write-Host "Backend PID : $($backendProc.Id)"
Write-Host "Frontend URL: $($env:SMART_MIRROR_FRONTEND_URL)"
Write-Host "Frontend mode: $frontendMode"
Write-Host "Python exe   : $pythonExe"
Write-Host "Logs directory: $runtimeDir"
