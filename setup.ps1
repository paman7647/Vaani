# Vaani Voice Assistant - Windows Setup Script
# Version 1.0
# Requires: Windows 10/11, PowerShell 5.1+

Write-Host ""
Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Vaani Voice Assistant Setup v1.0        ║" -ForegroundColor Cyan
Write-Host "║   Windows Installer                        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "✗ This script requires Administrator privileges" -ForegroundColor Red
    Write-Host "  Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Check PowerShell version
if ($PSVersionTable.PSVersion.Major -lt 5) {
    Write-Host "✗ PowerShell 5.1 or higher required" -ForegroundColor Red
    Write-Host "  Current version: $($PSVersionTable.PSVersion)" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Running with Administrator privileges" -ForegroundColor Green

# Check for Chocolatey
Write-Host ""
Write-Host "[1/7] Checking for Chocolatey package manager..." -ForegroundColor Blue
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "→ Installing Chocolatey..." -ForegroundColor Cyan
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    Write-Host "✓ Chocolatey installed" -ForegroundColor Green
} else {
    Write-Host "✓ Chocolatey found" -ForegroundColor Green
}

# Install Python
Write-Host ""
Write-Host "[2/7] Checking Python installation..." -ForegroundColor Blue
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (!$pythonCmd) {
    Write-Host "→ Installing Python 3.11..." -ForegroundColor Cyan
    choco install python311 -y
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Host "✓ Python installed" -ForegroundColor Green
} else {
    $pythonVersion = & python --version
    Write-Host "✓ $pythonVersion found" -ForegroundColor Green
}

# Install system dependencies
Write-Host ""
Write-Host "[3/7] Installing system dependencies..." -ForegroundColor Blue
Write-Host "→ Installing FFmpeg..." -ForegroundColor Cyan
choco install ffmpeg -y
Write-Host "→ Installing VLC Media Player..." -ForegroundColor Cyan
choco install vlc -y
Write-Host "✓ System dependencies installed" -ForegroundColor Green

# Refresh environment variables
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Create virtual environment
Write-Host ""
Write-Host "[4/7] Setting up Python virtual environment..." -ForegroundColor Blue
python -m pip install --upgrade pip
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip setuptools wheel
Write-Host "✓ Virtual environment created" -ForegroundColor Green

# Install Python packages
Write-Host ""
Write-Host "[5/7] Installing Python packages..." -ForegroundColor Blue
pip install -r requirements.txt
Write-Host "✓ Python packages installed" -ForegroundColor Green

# Download language models
Write-Host ""
Write-Host "[6/7] Downloading Vosk language models..." -ForegroundColor Blue

if (!(Test-Path "models")) {
    New-Item -ItemType Directory -Path "models" | Out-Null
}
Set-Location models

# Indian English Model
if (!(Test-Path "vosk-model-small-en-in-0.4")) {
    Write-Host "→ Downloading Indian English model (36MB)..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri "https://alphacephei.com/vosk/models/vosk-model-small-en-in-0.4.zip" -OutFile "en-in.zip"
    Expand-Archive -Path "en-in.zip" -DestinationPath "." -Force
    Remove-Item "en-in.zip"
    Write-Host "✓ Indian English model installed" -ForegroundColor Green
} else {
    Write-Host "✓ Indian English model already exists" -ForegroundColor Green
}

# Hindi Model
if (!(Test-Path "vosk-model-small-hi-0.22")) {
    Write-Host "→ Downloading Hindi model (42MB)..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri "https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip" -OutFile "hi.zip"
    Expand-Archive -Path "hi.zip" -DestinationPath "." -Force
    Remove-Item "hi.zip"
    Write-Host "✓ Hindi model installed" -ForegroundColor Green
} else {
    Write-Host "✓ Hindi model already exists" -ForegroundColor Green
}

# US English Model
if (!(Test-Path "vosk-model-small-en-us-0.15")) {
    Write-Host "→ Downloading US English model (39MB)..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip" -OutFile "en-us.zip"
    Expand-Archive -Path "en-us.zip" -DestinationPath "." -Force
    Remove-Item "en-us.zip"
    Write-Host "✓ US English model installed" -ForegroundColor Green
} else {
    Write-Host "✓ US English model already exists" -ForegroundColor Green
}

Set-Location ..

# Create .env file
Write-Host ""
Write-Host "[7/7] Creating environment configuration..." -ForegroundColor Blue
if (!(Test-Path ".env")) {
    @"
# Google Gemini API Key (Required)
# Get your key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_api_key_here

# Optional: Logging level
LOG_LEVEL=INFO
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✓ Created .env file" -ForegroundColor Green
    Write-Host "⚠ Remember to add your Google API key to .env" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Create run script
@"
@echo off
call venv\Scripts\activate.bat
python main.py
pause
"@ | Out-File -FilePath "run.bat" -Encoding ASCII

Write-Host ""
Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   Installation Complete! 🎉                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Add your API key: " -NoNewline; Write-Host "notepad .env" -ForegroundColor Cyan
Write-Host "2. Start Vaani: " -NoNewline; Write-Host ".\run.bat" -ForegroundColor Cyan
Write-Host "   Or: " -NoNewline; Write-Host ".\venv\Scripts\activate" -ForegroundColor Cyan
Write-Host "       " -NoNewline; Write-Host "python main.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Installed models:" -ForegroundColor White
Get-ChildItem models | Where-Object {$_.Name -like "vosk-*"} | ForEach-Object { Write-Host "  - $($_.Name)" }
Write-Host ""
