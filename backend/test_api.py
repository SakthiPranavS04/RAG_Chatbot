import os
import ollama
from config import settings

def test_api():
    print(f"Ollama Base URL: {settings.OLLAMA_BASE_URL}")
    print(f"Testing model: {settings.OLLAMA_MODEL}")
    client = ollama.Client(host=settings.OLLAMA_BASE_URL)
    try:
        print("Sending request...")
        response = client.generate(
            model=settings.OLLAMA_MODEL, 
            prompt="Hello",
            options={"num_ctx": 512}
        )
        print("Success! Response:")
        print(response.get('response'))
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    test_api()
