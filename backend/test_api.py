import ollama
from config import settings

def test_api():
    print(f"Ollama Base URL: {settings.OLLAMA_BASE_URL}")
    print(f"Testing model: {settings.OLLAMA_MODEL}")
    
    headers = {}
    if settings.OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {settings.OLLAMA_API_KEY}"
        
    client = ollama.Client(host=settings.OLLAMA_BASE_URL, headers=headers)
    
    try:
        response = client.generate(
            model=settings.OLLAMA_MODEL, 
            prompt="Hello",
            options={"num_ctx": 512}
        )
        print("Test passed! Received response:")
        print(response.get('response'))
    except Exception as e:
        print("Test failed. Error:", str(e))

if __name__ == "__main__":
    test_api()
