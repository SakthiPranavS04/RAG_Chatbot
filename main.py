import sys
import os
from utils import generate_answer, CHROMA_DB_DIR

def main():
    # Check if the database exists
    if not os.path.exists(CHROMA_DB_DIR):
        print("Knowledge base not found. Please run 'python ingest.py' first to build the database.")
        sys.exit(1)

    print("==================================================")
    print("      Welcome to the Local RAG CLI Chatbot!       ")
    print("==================================================")
    print("Type 'exit' or 'quit' to stop.")
    print("-" * 50)
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ")
            
            # Check for exit commands
            if user_input.strip().lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            # Skip empty inputs
            if not user_input.strip():
                continue
            
            print("Thinking...")
            
            # Generate and print the response
            response = generate_answer(user_input)
            print(f"Assistant: {response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
