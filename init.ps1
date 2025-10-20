#Requires -Version 5.1
<#
.SYNOPSIS
    fnwispr Development Environment Setup Script
.DESCRIPTION
    Sets up a Python virtual environment and installs all dependencies for fnwispr
.EXAMPLE
    .\init.ps1
#>

param(
    [switch]$SkipVenv = $false
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  fnwispr Development Environment Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "[1/4] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "       Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher from https://www.python.org" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Create virtual environment
Write-Host "[2/4] Setting up virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "       Virtual environment already exists, skipping creation" -ForegroundColor Gray
} else {
    try {
        python -m venv venv
        Write-Host "       Created virtual environment" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Activate virtual environment
Write-Host "[3/4] Installing dependencies..." -ForegroundColor Yellow
try {
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "       Activated virtual environment" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host "       Upgrading pip, setuptools, and wheel..." -ForegroundColor Gray
python -m pip install --quiet --upgrade pip setuptools wheel

# Install client dependencies
Write-Host "       Installing client dependencies..." -ForegroundColor Gray
try {
    pip install --quiet -r client\requirements.txt
    Write-Host "       ✓ Client dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to install client dependencies" -ForegroundColor Red
    exit 1
}

# Install server dependencies
Write-Host "       Installing server dependencies..." -ForegroundColor Gray
try {
    pip install --quiet -r server\requirements.txt
    Write-Host "       ✓ Server dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to install server dependencies" -ForegroundColor Red
    exit 1
}

# Install development dependencies (optional)
Write-Host "       Installing development tools..." -ForegroundColor Gray
if (Test-Path "requirements-dev.txt") {
    pip install --quiet -r requirements-dev.txt 2>$null
    Write-Host "       ✓ Dev tools installed" -ForegroundColor Green
} else {
    Write-Host "       (Optional dev requirements file not found)" -ForegroundColor Gray
}
Write-Host ""

# Create configuration files
Write-Host "[4/4] Creating configuration files..." -ForegroundColor Yellow

# Create client config from example
if (-not (Test-Path "client\config.json")) {
    if (Test-Path "client\config.example.json") {
        Copy-Item "client\config.example.json" "client\config.json"
        Write-Host "       Created client\config.json from example" -ForegroundColor Green
    }
} else {
    Write-Host "       client\config.json already exists" -ForegroundColor Gray
}

# Create .env file from example
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "       Created .env from example" -ForegroundColor Green
    }
} else {
    Write-Host "       .env already exists" -ForegroundColor Gray
}
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start the Whisper service:" -ForegroundColor White
Write-Host "   docker-compose up -d" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run the client:" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   cd client" -ForegroundColor Gray
Write-Host "   python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. (Optional) Run tests:" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host "   pytest tests\ -v" -ForegroundColor Gray
Write-Host ""
Write-Host "Virtual environment activation command:" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "To verify installation:" -ForegroundColor White
Write-Host '   python -c "import sounddevice; import fastapi; print(''All dependencies installed!'')"' -ForegroundColor Gray
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
