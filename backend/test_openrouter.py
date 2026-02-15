"""
Test script to verify OpenRouter API connection
"""
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")

def test_openrouter_connection():
    """Test the OpenRouter API connection"""
    print("Testing OpenRouter API connection...")
    print(f"Base URL: {OPENROUTER_BASE_URL}")
    print(f"Model: {OPENROUTER_MODEL}")
    print(f"API Key available: {'Yes' if OPENROUTER_API_KEY else 'No'}")

    if not OPENROUTER_API_KEY:
        print("ERROR: OpenRouter API key not found in environment variables!")
        return False

    try:
        # Initialize the client
        client = openai.OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
        )

        # Test the connection with a simple request
        print("\nSending test request to OpenRouter...")
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "user", "content": "Hello, are you working properly?"}
            ],
            max_tokens=50
        )

        print("✅ SUCCESS: OpenRouter API connection is working!")
        print(f"Response: {response.choices[0].message.content[:100]}...")
        return True

    except Exception as e:
        print(f"❌ ERROR: Failed to connect to OpenRouter API: {str(e)}")
        return False

if __name__ == "__main__":
    test_openrouter_connection()