from google import genai
from config import settings
import sys

client = genai.Client(api_key=settings.GEMINI_API_KEY)

try:
    print("Available models:")
    for m in client.models.list():
        print(m.name, m.supported_actions)
except Exception as e:
    print(f"Error listing models: {e}")
