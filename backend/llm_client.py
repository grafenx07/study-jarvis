"""
Local LLM Client for Ollama
Handles communication with self-hosted LLaMA/Mistral models
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "llama3")

def query_llm(prompt, model=DEFAULT_MODEL, max_tokens=1024, temperature=0.2, stream=False):
    """
    Query the local LLM via Ollama API

    Args:
        prompt: The prompt to send to the LLM
        model: Model name (llama3, mistral, etc.)
        max_tokens: Maximum tokens to generate (increased for better answers)
        temperature: Sampling temperature (0.0 to 1.0) - lower is more focused/accurate
        stream: Whether to stream the response

    Returns:
        Generated text response
    """
    try:
        url = f"{OLLAMA_URL}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "top_p": 0.85,  # Slightly lower for more focused responses
                "top_k": 40,  # Limit vocabulary for consistency
                "repeat_penalty": 1.15,  # Stronger penalty to reduce repetition
                "num_ctx": 4096,  # Increased context window
                "stop": ["</s>", "Human:", "User:", "Student:"],  # Stop sequences
            }
        }

        response = requests.post(url, json=payload, timeout=180)  # Increased timeout
        response.raise_for_status()

        if stream:
            # Handle streaming response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        full_response += data["response"]
                    if data.get("done", False):
                        break
            return full_response
        else:
            # Handle regular response
            data = response.json()
            return data.get("response", "")

    except requests.exceptions.ConnectionError:
        return "❌ Error: Cannot connect to Ollama. Make sure Ollama is running (ollama serve)."
    except requests.exceptions.Timeout:
        return "❌ Error: Request timed out. The model might be too large or slow."
    except Exception as e:
        return f"❌ Error querying LLM: {str(e)}"

def build_study_prompt(context_chunks, user_question, mode="answer"):
    """
    Build a structured prompt for the study assistant

    Args:
        context_chunks: List of relevant note chunks
        user_question: User's question
        mode: "answer", "summarize", "quiz", or "flashcard"

    Returns:
        Formatted prompt string
    """
    if mode == "answer":
        context_block = "\n\n---\n\n".join(context_chunks) if context_chunks else "No relevant notes found."

        prompt = f"""You are Study Jarvis, an expert study assistant. Answer the question using ONLY the information from the notes below.

===== STUDENT'S NOTES =====
{context_block}

===== QUESTION =====
{user_question}

===== YOUR TASK =====
1. Read the notes carefully and find relevant information
2. Answer the question clearly and directly
3. Use simple, clear language
4. Include specific details from the notes
5. If you mention a fact, cite the source file in parentheses like (source: filename.pdf)
6. After your answer, add a "SOURCES:" section listing which files you used

Remember: Only use information from the notes above. Do not add external knowledge.

===== ANSWER ====="""

    elif mode == "summarize":
        context_block = "\n\n".join(context_chunks)

        prompt = f"""You are Study Jarvis. Your task is to create a clear, well-organized summary.

===== NOTES TO SUMMARIZE =====
{context_block}

===== YOUR TASK =====
Create a summary that includes:
• Main topics covered
• Key concepts and definitions
• Important facts and details
• Key takeaways for studying

Write in bullet points for clarity.

===== SUMMARY ====="""

    elif mode == "quiz":
        context_block = "\n\n".join(context_chunks)

        prompt = f"""You are Study Jarvis. Based on these notes, create {user_question} multiple-choice questions to test understanding.

Notes:
{context_block}

Format each question as:
Q[number]. [Question]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct Answer: [Letter]

Questions:"""

    elif mode == "flashcard":
        context_block = "\n\n".join(context_chunks)

        prompt = f"""You are Study Jarvis. Create {user_question} flashcards from these notes.

Notes:
{context_block}

Format each flashcard as:
Card [number]:
Front: [Question]
Back: [Answer]

Flashcards:"""

    else:
        prompt = f"Context: {' '.join(context_chunks)}\n\nQuestion: {user_question}\n\nAnswer:"

    return prompt

def check_ollama_status():
    """Check if Ollama is running and which models are available"""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        response.raise_for_status()
        models = response.json().get("models", [])
        return {
            "status": "online",
            "models": [m["name"] for m in models]
        }
    except:
        return {
            "status": "offline",
            "models": []
        }

if __name__ == "__main__":
    # Test LLM connection
    print("Testing Ollama connection...")
    status = check_ollama_status()
    print(f"Status: {status['status']}")
    if status['models']:
        print(f"Available models: {', '.join(status['models'])}")
    else:
        print("No models found. Run: ollama pull llama3")

    # Test query
    if status['status'] == 'online' and status['models']:
        print("\nTesting query...")
        response = query_llm("Say 'Hello, I am Study Jarvis!' in one sentence.")
        print(f"Response: {response}")
