from google import genai
from config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

print("Testing models...")

try:
    response = client.models.generate_content(
        model='gemini-1.5-pro',
        contents="Hello"
    )
    print("Success: gemini-1.5-pro")
except Exception as e:
    print(f"Error with pro: {e}")

try:
    response = client.models.generate_content(
        model='gemini-1.5-flash-8b',
        contents="Hello"
    )
    print("Success: gemini-1.5-flash-8b")
except Exception as e:
    print(f"Error with 8b: {e}")

try:
    response = client.models.generate_content(
        model='gemini-1.0-pro',
        contents="Hello"
    )
    print("Success: gemini-1.0-pro")
except Exception as e:
    print(f"Error with 1.0: {e}")
