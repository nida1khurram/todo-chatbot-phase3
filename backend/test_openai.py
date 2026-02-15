"""
Test script to verify OpenAI API connection
"""
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_connection(api_key=None):
    """Test the OpenAI API connection"""
    # Use provided API key or get from environment
    if api_key:
        openai_api_key = api_key
    else:
        openai_api_key = os.getenv("OPENAI_API_KEY")

    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    print("Testing OpenAI API connection...")
    print(f"Base URL: {openai_base_url}")
    print(f"Model: {openai_model}")
    print(f"API Key available: {'Yes' if openai_api_key else 'No'}")

    if not openai_api_key:
        print("ERROR: OpenAI API key not provided or found in environment variables!")
        print("Please provide your OpenAI API key or set OPENAI_API_KEY environment variable.")
        return False

    try:
        # Initialize the client
        client = openai.OpenAI(
            api_key=openai_api_key,
            base_url=openai_base_url,
        )

        # Test the connection with a simple request
        print("\\nSending test request to OpenAI...")
        response = client.chat.completions.create(
            model=openai_model,
            messages=[
                {"role": "user", "content": "Hello, are you working properly?"}
            ],
            max_tokens=50
        )

        print("SUCCESS: OpenAI API connection is working!")
        print(f"Response: {response.choices[0].message.content[:100]}...")
        return True

    except Exception as e:
        print(f"ERROR: Failed to connect to OpenAI API: {str(e)}")
        return False

if __name__ == "__main__":
    # You can pass your API key here for testing
    # test_openai_connection("your-api-key-here")

    # Or run without key to check environment
    test_openai_connection()