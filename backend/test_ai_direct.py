"""
Test script to directly test the OpenAI API connection
"""
import asyncio
from src.config.ai_config import AIConfig
from src.services.ai_agent_service import AIAgentService
from src.mcp_server.tools import get_mcp_tools_definitions

async def test_ai_connection():
    print("Testing direct AI API connection...")

    try:
        # Create the AI service
        ai_service = AIAgentService()

        print(f"Model: {ai_service.model}")

        # Get the tools definitions
        tools = get_mcp_tools_definitions()
        print(f"Number of tools: {len(tools)}")

        # Test with a simple message
        messages = [
            {"role": "user", "content": "Hello, are you working?"}
        ]

        print("Attempting to call OpenAI API...")
        result = await ai_service.run_conversation(messages, tools)

        print("SUCCESS: AI API is working!")
        print(f"Response type: {result['type']}")
        print(f"Response content: {result.get('content', 'No content')}")

        return True

    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    asyncio.run(test_ai_connection())