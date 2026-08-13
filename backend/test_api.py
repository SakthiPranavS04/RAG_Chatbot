import groq
from config import settings

def test_api():
    print(f"Testing model: {settings.LLM_MODEL}")
    
    if not settings.GROQ_API_KEY:
        print("Test failed. GROQ_API_KEY is missing in .env")
        return
        
    client = groq.Groq(api_key=settings.GROQ_API_KEY)
    
    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL, 
            messages=[
                {"role": "user", "content": "Hello! Reply with 'Test passed' if you can read this."}
            ],
            max_tokens=1024
        )
        print("Test passed! Received response:")
        print(response.choices[0].message.content if response.choices else '')
    except Exception as e:
        print("Test failed. Error:", str(e))

if __name__ == "__main__":
    test_api()
