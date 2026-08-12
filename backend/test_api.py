import anthropic
from config import settings

def test_api():
    print(f"Testing model: {settings.CLAUDE_MODEL}")
    
    if not settings.ANTHROPIC_API_KEY:
        print("Test failed. ANTHROPIC_API_KEY is missing.")
        return
        
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    try:
        response = client.messages.create(
            model=settings.CLAUDE_MODEL, 
            max_tokens=1024,
            messages=[
                {"role": "user", "content": "Hello! Reply with 'Test passed' if you can read this."}
            ]
        )
        print("Test passed! Received response:")
        print(response.content[0].text if response.content else '')
    except Exception as e:
        print("Test failed. Error:", str(e))

if __name__ == "__main__":
    test_api()
