"""
Test script to verify OpenAI API connection using system environment variables
"""
import os
import openai
from dotenv import load_dotenv

# Load environment variables but prioritize system environment
load_dotenv()

def test_openai_connection():
    """Test the OpenAI API connection using only system environment variables"""
    # Only check system environment, no .env fallback
    system_api_key = os.environ.get("OPENAI_API_KEY")
    env_api_key = os.getenv("OPENAI_API_KEY")  # This will still work but we won't use it

    print("OpenAI API Configuration Check:")
    print(f"System Environment OPENAI_API_KEY: {'Found' if system_api_key else 'Not found'}")
    print(f"From .env file: {'Found' if env_api_key else 'Not found (but not used)'}")

    # Only use system environment variable, no fallback to .env
    openai_api_key = system_api_key
    openai_base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

    print(f"Base URL: {openai_base_url}")
    print(f"Model: {openai_model}")
    print(f"Using API Key: {'Yes' if openai_api_key else 'No'}")

    if not openai_api_key:
        print("ERROR: OpenAI API key not found in system environment or .env file!")
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
        print(f"Response: {response.choices[0].message.content}")
        return True

    except Exception as e:
        print(f"ERROR: Failed to connect to OpenAI API: {str(e)}")
        return False

if __name__ == "__main__":
    test_openai_connection()