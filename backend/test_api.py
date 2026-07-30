import os
from config import settings
from google import genai

def test_api():
    api_key = settings.GEMINI_API_KEY
    print(f"API Key: {api_key[:10]}...")
    client = genai.Client(api_key=api_key)
    try:
        print("Sending request...")
        models = client.models.list_models()
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    test_api()
