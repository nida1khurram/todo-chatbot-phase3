"""
Test script to test the AI Agent Manager specifically
"""
import asyncio
from src.services.ai_agent_manager import AIAgentManager

async def test_ai_manager():
    print("Testing AI Agent Manager...")

    try:
        # Create the AI agent manager
        ai_manager = AIAgentManager()

        print("Attempting to process message through AI Manager...")

        # Test with a simple message
        result = await ai_manager.process_message(
            user_id="1",
            message="Hello, are you working?",
            conversation_history=[]
        )

        print("SUCCESS: AI Manager is working!")
        print(f"Result type: {result['type']}")
        print(f"Result content: {result.get('content', 'No content')}")

        return True

    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_ai_manager())