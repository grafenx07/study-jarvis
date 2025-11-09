# Study Jarvis Setup Script for Windows PowerShell
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Study Jarvis Setup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonCmd = "py -3.12"
$pythonVersion = & py -3.12 --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "ERROR Python 3.12 not found! Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Navigate to backend directory
Set-Location -Path "backend"

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "OK Virtual environment already exists" -ForegroundColor Green
} else {
    & py -3.12 -m venv venv
    Write-Host "OK Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "OK Dependencies installed" -ForegroundColor Green

# Setup .env file
Write-Host "`nSetting up environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "OK .env file already exists" -ForegroundColor Green
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "OK Created .env file from template" -ForegroundColor Green
    Write-Host "WARNING Please edit .env and add your Pinecone API key" -ForegroundColor Yellow
}

# Check Ollama installation
Write-Host "`nChecking Ollama installation..." -ForegroundColor Yellow
$ollamaCheck = Get-Command ollama -ErrorAction SilentlyContinue
$ollamaPath = $null

if ($ollamaCheck) {
    $ollamaPath = $ollamaCheck.Source
} elseif (Test-Path "D:\Ollama\ollama.exe") {
    $ollamaPath = "D:\Ollama\ollama.exe"
    Write-Host "OK Ollama found at D:\Ollama" -ForegroundColor Green
}

if ($ollamaPath) {
    $ollamaVersion = & $ollamaPath --version 2>&1
    Write-Host "OK Ollama version: $ollamaVersion" -ForegroundColor Green

    Write-Host "`nChecking for AI models..." -ForegroundColor Yellow
    $ollamaList = & $ollamaPath list 2>&1
    if ($ollamaList -match "llama3|gemma") {
        Write-Host "OK AI model found" -ForegroundColor Green
    } else {
        Write-Host "WARNING No models found" -ForegroundColor Yellow
        Write-Host "Run manually: ollama pull llama3" -ForegroundColor Cyan
    }
} else {
    Write-Host "ERROR Ollama not found!" -ForegroundColor Red
    Write-Host "Install from: https://ollama.com/download" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "1. Edit backend/.env and add your Pinecone API key" -ForegroundColor White
Write-Host "2. Start Ollama: D:\Ollama\ollama.exe serve" -ForegroundColor White
Write-Host "3. Start backend: uvicorn app:app --reload" -ForegroundColor White
Write-Host "4. Open frontend/index.html in your browser" -ForegroundColor White
Write-Host ""
Write-Host "Quick test:" -ForegroundColor Green
Write-Host "python ingest_notes.py ../sample_notes.txt 'Data Structures'" -ForegroundColor White
Write-Host ""
Write-Host "Happy learning!" -ForegroundColor Cyan
