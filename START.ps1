# PowerShell Startup Script for AgriWaste to Worth
# Run the full project with frontend and backend

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "   AgriWaste to Worth - Full Project Startup" -ForegroundColor Green
Write-Host "   Frontend + Backend + AI System + Chatbot" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.8+" -ForegroundColor Red
    Write-Host "Download from: https://www.python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Activate virtual environment if it exists
if (Test-Path "venv/Scripts/Activate.ps1") {
    Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Cyan
    & "venv/Scripts/Activate.ps1"
    Write-Host "[OK] Virtual environment activated" -ForegroundColor Green
    Write-Host ""
}

# Show system info
Write-Host "[INFO] System Status:" -ForegroundColor Cyan
python -c "import sys; print(f'  - Python: {sys.version.split()[0]}')"
Write-Host ""

# Start server
Write-Host "[INFO] Starting Flask Server..." -ForegroundColor Cyan
Write-Host "[INFO] This will take a moment to initialize..." -ForegroundColor Cyan
Write-Host ""

python startup.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Failed to start server" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}
