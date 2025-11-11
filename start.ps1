# Start Ollama in background
Start-Process -FilePath "D:\Ollama\ollama.exe" -ArgumentList "serve" -WindowStyle Minimized

# Wait for Ollama to start
Start-Sleep -Seconds 3

# Start Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\grafe\OneDrive\Desktop\Internship Training\personal-jarvis\backend'; .\venv\Scripts\Activate.ps1; python app.py"

# Wait for Backend to start
Start-Sleep -Seconds 5

# Open Frontend
Start-Process "C:\Users\grafe\OneDrive\Desktop\Internship Training\personal-jarvis\frontend\index.html"
