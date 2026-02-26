param(
    [switch]$SkipInstall,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendPath = Join-Path $projectRoot 'backend'
$frontendPath = Join-Path $projectRoot 'frontend'
$venvPython = Join-Path $backendPath '.venv\Scripts\python.exe'

function Test-CommandExists {
    param([string]$CommandName)
    return $null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

if (-not (Test-Path $backendPath)) {
    throw "Backend directory not found: $backendPath"
}

if (-not (Test-Path $frontendPath)) {
    throw "Frontend directory not found: $frontendPath"
}

if (-not (Test-CommandExists 'python')) {
    throw 'python was not found. Please install Python and add it to PATH.'
}

if (-not (Test-CommandExists 'npm')) {
    throw 'npm was not found. Please install Node.js (with npm) and add it to PATH.'
}

if (-not (Test-Path $venvPython)) {
    Write-Host 'Creating backend virtual environment...'
    Push-Location $backendPath
    try {
        python -m venv .venv
    }
    finally {
        Pop-Location
    }
}

if (-not $SkipInstall) {
    Write-Host 'Installing/updating backend dependencies...'
    Push-Location $backendPath
    try {
        & $venvPython -m pip install -r requirements.txt
    }
    finally {
        Pop-Location
    }

    if (-not (Test-Path (Join-Path $frontendPath 'node_modules'))) {
        Write-Host 'Installing frontend dependencies...'
        Push-Location $frontendPath
        try {
            npm install
        }
        finally {
            Pop-Location
        }
    }
}

$backendCommand = "Set-Location '$backendPath'; & '$venvPython' -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
$frontendCommand = "Set-Location '$frontendPath'; npm run dev"

if ($DryRun) {
    Write-Host 'DryRun mode enabled: no new windows will be started.'
    Write-Host "Backend command: $backendCommand"
    Write-Host "Frontend command: $frontendCommand"
    return
}

Write-Host 'Starting backend service window...'
Start-Process powershell -ArgumentList @(
    '-NoExit',
    '-ExecutionPolicy', 'Bypass',
    '-Command',
    "$host.UI.RawUI.WindowTitle = 'stock-agent backend'; $backendCommand"
)

Write-Host 'Starting frontend service window...'
Start-Process powershell -ArgumentList @(
    '-NoExit',
    '-ExecutionPolicy', 'Bypass',
    '-Command',
    "$host.UI.RawUI.WindowTitle = 'stock-agent frontend'; $frontendCommand"
)

Write-Host ''
Write-Host 'Started:'
Write-Host '- Backend: http://localhost:8000/docs'
Write-Host '- Frontend: http://localhost:5173'
Write-Host ''
Write-Host 'If dependencies are already installed, run: .\start.ps1 -SkipInstall'
