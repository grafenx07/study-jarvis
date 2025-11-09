# Study Jarvis - Quick Start Guide

## 🚀 Get Started in 5 Minutes!

### 1. Setup Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure Environment

Create `backend/.env`:
```
PINECONE_API_KEY=your_key_here
PINECONE_REGION=us-east-1
OLLAMA_URL=http://localhost:11434
LLM_MODEL=llama3
```

### 3. Install Ollama & Pull Model

Download Ollama from https://ollama.com/download

```powershell
ollama pull llama3
ollama serve
```

### 4. Start Backend

```powershell
# In backend folder
uvicorn app:app --reload
```

### 5. Upload Sample Notes

```powershell
# Copy sample notes to backend folder first
python ingest_notes.py ..\sample_notes.txt "Data Structures" "Overview"
```

### 6. Open Frontend

Open `frontend/index.html` in your browser or use VS Code Live Server.

### 7. Test It!

Try these questions:
- "What is the difference between merge sort and quick sort?"
- "Explain binary search trees"
- "Generate 5 quiz questions on sorting algorithms"

## 🎯 Common Commands

**Upload notes:**
```powershell
python ingest_notes.py notes.pdf "Subject" "Chapter"
```

**Start backend:**
```powershell
uvicorn app:app --reload
```

**Test connections:**
```powershell
python pinecone_client.py
python llm_client.py
```

## ⚠️ Troubleshooting

**Ollama not found:**
```powershell
ollama serve
```

**Pinecone error:**
- Check API key in `.env`
- Verify region is correct

**Import errors:**
```powershell
pip install -r requirements.txt --upgrade
```

## 📚 Next Steps

1. Upload your own study materials
2. Experiment with different modes (summarize, quiz, flashcard)
3. Customize the prompts in `llm_client.py`
4. Try different LLM models (mistral, llama2, etc.)

Happy studying! 🎓
