# Study Jarvis - Command Cheat Sheet

## 🚀 Quick Commands

### Initial Setup (One Time)

```powershell
# Navigate to project
cd personal-jarvis\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Setup environment
copy .env.example .env
# Then edit .env with your Pinecone API key
```

### Ollama Commands

```powershell
# Install LLaMA 3
ollama pull llama3

# Install Mistral (alternative)
ollama pull mistral

# List installed models
ollama list

# Start Ollama server
ollama serve

# Test model directly
ollama run llama3 "Hello, how are you?"
```

### Daily Usage

```powershell
# 1. Activate virtual environment
cd personal-jarvis\backend
.\venv\Scripts\Activate.ps1

# 2. Start backend server
uvicorn app:app --reload

# 3. In another terminal: Start Ollama (if not running)
ollama serve

# 4. Open frontend
# Open frontend/index.html in your browser
```

### Upload Notes

```powershell
# Upload single file
python ingest_notes.py "path\to\notes.pdf" "Subject Name" "Chapter Name"

# Examples:
python ingest_notes.py "..\sample_notes.txt" "Data Structures"
python ingest_notes.py "C:\Study\OS.pdf" "Operating Systems" "Chapter 1"
python ingest_notes.py "lecture.docx" "Databases" "SQL"

# Upload all files in a directory
python ingest_notes.py "C:\Study\Notes" "Computer Science"
```

### Testing & Debugging

```powershell
# Run system tests
python test_system.py

# Test Pinecone connection
python pinecone_client.py

# Test Ollama connection
python llm_client.py

# Check backend API
# Visit: http://localhost:8000
# Visit: http://localhost:8000/docs (API documentation)
```

### API Testing (using curl or PowerShell)

```powershell
# Check health
curl http://localhost:8000/

# Check status
curl http://localhost:8000/status

# Upload file (PowerShell)
$file = Get-Item "notes.pdf"
$uri = "http://localhost:8000/upload"
$form = @{
    file = $file
    subject = "Math"
    chapter = "Calculus"
}
Invoke-RestMethod -Uri $uri -Method Post -Form $form

# Send chat message
$body = @{
    message = "Explain merge sort"
    mode = "answer"
    top_k = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Body $body -ContentType "application/json"
```

### Environment Variables (.env)

```bash
# Required
PINECONE_API_KEY=your_api_key_here
PINECONE_REGION=us-east-1

# Optional (defaults shown)
PINECONE_CLOUD=aws
OLLAMA_URL=http://localhost:11434
LLM_MODEL=llama3
```

### Package Management

```powershell
# Update all packages
pip install -r requirements.txt --upgrade

# Install specific package
pip install fastapi

# List installed packages
pip list

# Check for outdated packages
pip list --outdated
```

### Git Commands (if using version control)

```powershell
# Initialize repo
git init

# Add files (respects .gitignore)
git add .

# Commit
git commit -m "Initial commit: Study Jarvis"

# Add remote
git remote add origin https://github.com/yourusername/study-jarvis.git

# Push
git push -u origin main
```

### Troubleshooting Commands

```powershell
# Check Python version
python --version

# Check pip version
pip --version

# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check if backend is running
curl http://localhost:8000/

# Kill process on port (if port is busy)
# Find process
netstat -ano | findstr :8000
# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Performance Tuning

```powershell
# Use different embedding model (in pinecone_client.py and app.py)
# all-MiniLM-L6-v2      → Fast, 384 dims
# all-mpnet-base-v2     → Better, 768 dims
# all-MiniLM-L12-v2     → Balanced

# Use different LLM model
ollama pull mistral      # Faster, 7B
ollama pull llama3       # Balanced, 8B
ollama pull llama2       # Alternative, 7B
```

### Development Commands

```powershell
# Run backend with auto-reload
uvicorn app:app --reload

# Run backend on different port
uvicorn app:app --reload --port 8080

# Run backend with detailed logs
uvicorn app:app --reload --log-level debug

# Format code (if black installed)
black *.py

# Lint code (if pylint installed)
pylint *.py
```

### Cleanup Commands

```powershell
# Remove virtual environment
Remove-Item -Recurse -Force venv

# Clear Python cache
Get-ChildItem -Path . -Filter "__pycache__" -Recurse | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Filter "*.pyc" -Recurse | Remove-Item -Force

# Clear Pinecone index (⚠️ DANGER: Deletes all data)
python -c "import pinecone_client; pinecone_client.delete_all()"
```

### Useful Keyboard Shortcuts

**In Terminal:**
- `Ctrl + C` - Stop running process
- `Ctrl + Z` - Suspend process
- `↑` / `↓` - Navigate command history
- `Tab` - Auto-complete

**In VS Code:**
- `Ctrl + ` ` - Toggle terminal
- `Ctrl + Shift + P` - Command palette
- `F5` - Start debugging
- `Ctrl + B` - Toggle sidebar

## 📋 Common Workflows

### Daily Study Session

```powershell
# 1. Start services
cd personal-jarvis\backend
.\venv\Scripts\Activate.ps1
uvicorn app:app --reload

# In another terminal:
ollama serve

# 2. Open frontend in browser
start ..\frontend\index.html

# 3. Use the app!
```

### Upload New Notes

```powershell
cd personal-jarvis\backend
.\venv\Scripts\Activate.ps1
python ingest_notes.py "new_notes.pdf" "Subject" "Topic"
```

### Generate Study Materials

In the web UI:
1. Select mode: Quiz or Flashcard
2. Type: "10 questions on [topic]"
3. Copy results for studying

### Clear and Restart

```powershell
# Stop all services (Ctrl+C in each terminal)

# Clear database (if needed)
python -c "import pinecone_client; pinecone_client.delete_all()"

# Re-upload notes
python ingest_notes.py "notes.pdf" "Subject"

# Restart services
ollama serve
uvicorn app:app --reload
```

## 🎯 Pro Tips

1. **Keep Ollama running in background** - Start once, use all day
2. **Use descriptive subjects** - Makes filtering easier later
3. **Upload chapter by chapter** - Better organization
4. **Test with sample notes first** - Verify everything works
5. **Check status indicators** - Ensure green before using
6. **Use quiz mode for review** - Great before exams
7. **Create flashcards daily** - Spaced repetition works!

## 🆘 Quick Fixes

**"Cannot connect to Ollama"**
```powershell
ollama serve
```

**"Pinecone authentication failed"**
- Check .env file has correct API key
- No spaces in .env file

**"Module not found"**
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**"Port already in use"**
```powershell
uvicorn app:app --reload --port 8080
# Update frontend index.html to use :8080
```

**"No relevant context found"**
```powershell
python ingest_notes.py "notes.txt" "Subject"
```

## 📞 Support Links

- Ollama: https://ollama.com/
- Pinecone: https://www.pinecone.io/
- FastAPI Docs: https://fastapi.tiangolo.com/
- Python: https://www.python.org/

---

**Keep this file handy for quick reference!** 📌
