# Start API Server
# Run this script to start the Medical Diagnosis System API server

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "MEDICAL DIAGNOSIS SYSTEM - API SERVER" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path ".venv") {
    Write-Host "[✓] Virtual environment found" -ForegroundColor Green
    Write-Host "[*] Activating virtual environment..." -ForegroundColor Yellow
    .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "[!] Virtual environment not found" -ForegroundColor Red
    Write-Host "[*] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    Write-Host "[*] Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "[*] Checking environment variables..." -ForegroundColor Yellow

if (Test-Path ".env") {
    Write-Host "[✓] .env file found" -ForegroundColor Green
} else {
    Write-Host "[!] .env file not found - Supabase features may not work" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Starting API Server..." -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "API URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Frontend: Open index.html in your browser" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the API server
python api_server.py
