"""
System Test Script
Run this to verify all components are working correctly
"""
import sys
import os

# Add color support for Windows
try:
    import colorama
    colorama.init()
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
except:
    GREEN = RED = YELLOW = BLUE = RESET = ''

def print_test(test_name, status, message=""):
    """Print test result with color"""
    symbol = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
    print(f"{symbol} {test_name}: {message}")
    return status

def test_imports():
    """Test if all required packages are installed"""
    print(f"\n{BLUE}Testing Python Packages...{RESET}")
    all_good = True

    packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('sentence_transformers', 'Sentence Transformers'),
        ('pinecone', 'Pinecone'),
        ('PyPDF2', 'PyPDF2'),
        ('docx', 'python-docx'),
        ('dotenv', 'python-dotenv'),
        ('pydantic', 'Pydantic'),
    ]

    for package, name in packages:
        try:
            __import__(package)
            print_test(name, True, "installed")
        except ImportError:
            print_test(name, False, "NOT installed")
            all_good = False

    return all_good

def test_environment():
    """Test environment configuration"""
    print(f"\n{BLUE}Testing Environment Configuration...{RESET}")
    all_good = True

    if os.path.exists('.env'):
        print_test("Environment file", True, ".env exists")

        from dotenv import load_dotenv
        load_dotenv()

        # Check Pinecone config
        api_key = os.getenv('PINECONE_API_KEY')
        if api_key and api_key != 'your_pinecone_api_key_here':
            print_test("Pinecone API key", True, "configured")
        else:
            print_test("Pinecone API key", False, "not configured in .env")
            all_good = False

        # Check Ollama config
        ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        print_test("Ollama URL", True, ollama_url)

    else:
        print_test("Environment file", False, ".env not found")
        all_good = False

    return all_good

def test_ollama():
    """Test Ollama connection"""
    print(f"\n{BLUE}Testing Ollama LLM...{RESET}")

    try:
        import requests
        from dotenv import load_dotenv
        load_dotenv()

        ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)

        if response.status_code == 200:
            print_test("Ollama server", True, "running")

            models = response.json().get('models', [])
            if models:
                model_names = [m['name'] for m in models]
                print_test("Models available", True, f"{len(models)} model(s)")
                for name in model_names:
                    print(f"  • {name}")
                return True
            else:
                print_test("Models available", False, "no models found")
                print(f"{YELLOW}  Run: ollama pull llama3{RESET}")
                return False
        else:
            print_test("Ollama server", False, f"HTTP {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print_test("Ollama server", False, "not running")
        print(f"{YELLOW}  Run: ollama serve{RESET}")
        return False
    except Exception as e:
        print_test("Ollama server", False, str(e))
        return False

def test_pinecone():
    """Test Pinecone connection"""
    print(f"\n{BLUE}Testing Pinecone Vector Database...{RESET}")

    try:
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv('PINECONE_API_KEY')

        if not api_key or api_key == 'your_pinecone_api_key_here':
            print_test("Pinecone connection", False, "API key not configured")
            return False

        from pinecone import Pinecone
        pc = Pinecone(api_key=api_key)

        print_test("Pinecone authentication", True, "connected")

        # Check indexes
        indexes = [index.name for index in pc.list_indexes()]
        if indexes:
            print_test("Pinecone indexes", True, f"{len(indexes)} index(es)")
            for idx in indexes:
                print(f"  • {idx}")
        else:
            print_test("Pinecone indexes", True, "no indexes yet (will be created)")

        return True

    except Exception as e:
        print_test("Pinecone connection", False, str(e))
        return False

def test_embedding_model():
    """Test embedding model loading"""
    print(f"\n{BLUE}Testing Embedding Model...{RESET}")

    try:
        from sentence_transformers import SentenceTransformer

        print(f"{YELLOW}Loading model (this may take a moment)...{RESET}")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print_test("Embedding model", True, "all-MiniLM-L6-v2 loaded")

        # Test encoding
        test_text = "This is a test sentence."
        embedding = model.encode([test_text])[0]
        print_test("Embedding generation", True, f"dimension: {len(embedding)}")

        return True

    except Exception as e:
        print_test("Embedding model", False, str(e))
        return False

def test_file_reading():
    """Test file reading capabilities"""
    print(f"\n{BLUE}Testing File Reading...{RESET}")
    all_good = True

    # Test sample notes
    if os.path.exists('../sample_notes.txt'):
        print_test("Sample notes", True, "found")
        try:
            with open('../sample_notes.txt', 'r', encoding='utf-8') as f:
                content = f.read()
            print_test("Text file reading", True, f"{len(content)} characters")
        except Exception as e:
            print_test("Text file reading", False, str(e))
            all_good = False
    else:
        print_test("Sample notes", False, "not found")
        all_good = False

    return all_good

def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*50}{RESET}")
    print(f"{BLUE}  Study Jarvis System Test{RESET}")
    print(f"{BLUE}{'='*50}{RESET}")

    results = []

    results.append(("Python Packages", test_imports()))
    results.append(("Environment", test_environment()))
    results.append(("Ollama LLM", test_ollama()))
    results.append(("Pinecone DB", test_pinecone()))
    results.append(("Embedding Model", test_embedding_model()))
    results.append(("File Reading", test_file_reading()))

    # Summary
    print(f"\n{BLUE}{'='*50}{RESET}")
    print(f"{BLUE}  Test Summary{RESET}")
    print(f"{BLUE}{'='*50}{RESET}")

    passed = sum(1 for _, status in results if status)
    total = len(results)

    for name, status in results:
        symbol = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
        print(f"{symbol} {name}")

    print(f"\n{BLUE}Result: {passed}/{total} tests passed{RESET}")

    if passed == total:
        print(f"\n{GREEN}🎉 All systems operational! Ready to start.{RESET}")
        print(f"\nNext steps:")
        print(f"1. Start backend: uvicorn app:app --reload")
        print(f"2. Open frontend/index.html in browser")
        print(f"3. Upload notes or use sample_notes.txt")
    else:
        print(f"\n{RED}⚠ Some systems need attention. Check errors above.{RESET}")
        print(f"\nCommon fixes:")
        print(f"• Missing packages: pip install -r requirements.txt")
        print(f"• Ollama not running: ollama serve")
        print(f"• No models: ollama pull llama3")
        print(f"• Pinecone: Add API key to .env")

    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test interrupted by user.{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Unexpected error: {e}{RESET}")
        sys.exit(1)
