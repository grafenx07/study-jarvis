# Test Different Models - Compare Quality
# Run this after installing new models to see which performs best

Write-Host "`n🧪 MODEL COMPARISON TEST" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray

# Test question
$testQuestion = "What is a binary search tree and what are its key properties?"

Write-Host "`n📝 Test Question:" -ForegroundColor Yellow
Write-Host $testQuestion -ForegroundColor White

# Function to test a model
function Test-Model {
    param($modelName)

    Write-Host "`n" + ("=" * 60) -ForegroundColor Gray
    Write-Host "🤖 Testing Model: $modelName" -ForegroundColor Green
    Write-Host ("=" * 60) -ForegroundColor Gray

    try {
        # Update .env temporarily
        $envPath = "C:\Users\grafe\OneDrive\Desktop\Internship Training\personal-jarvis\backend\.env"
        $envContent = Get-Content $envPath
        $envContent = $envContent -replace 'LLM_MODEL=.*', "LLM_MODEL=$modelName"
        $envContent | Set-Content $envPath

        # Wait a moment for .env to update
        Start-Sleep -Seconds 2

        # Make API call
        $body = @{
            message = $testQuestion
            mode = "answer"
            top_k = 10
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/chat" -Method POST -Body $body -ContentType "application/json" -ErrorAction Stop

        Write-Host "`n📖 Answer:" -ForegroundColor Cyan
        Write-Host $response.answer -ForegroundColor White
        Write-Host "`n📚 Sources Used:" -ForegroundColor Magenta
        $response.sources | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }

    } catch {
        Write-Host "`n❌ Error testing $modelName : $_" -ForegroundColor Red
    }
}

# Check which models are available
Write-Host "`n🔍 Checking installed models..." -ForegroundColor Cyan
$installedModels = & "D:\Ollama\ollama.exe" list | Select-Object -Skip 1 | ForEach-Object {
    ($_ -split '\s+')[0]
}

Write-Host "Installed models:" -ForegroundColor Gray
$installedModels | ForEach-Object { Write-Host "  ✓ $_" -ForegroundColor Green }

# Test each installed model
foreach ($model in $installedModels) {
    if ($model -and $model.Trim() -ne "") {
        Test-Model -modelName $model
        Start-Sleep -Seconds 3
    }
}

Write-Host "`n" + ("=" * 60) -ForegroundColor Gray
Write-Host "✅ COMPARISON COMPLETE!" -ForegroundColor Green
Write-Host ("=" * 60) -ForegroundColor Gray
Write-Host "`n💡 TIP: The model with more specific, accurate information" -ForegroundColor Yellow
Write-Host "         and fewer hallucinations is the best choice!" -ForegroundColor Yellow
Write-Host "`n📝 Update your .env file with: LLM_MODEL=<best_model_name>`n" -ForegroundColor Cyan
