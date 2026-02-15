"""
Test script to test the AI Agent with tools (similar to how the chat endpoint uses it)
"""
import asyncio
from src.services.ai_agent_manager import AIAgentManager

async def test_ai_with_tools():
    print("Testing AI Agent Manager with tools (like chat endpoint)...")

    try:
        # Create the AI agent manager
        ai_manager = AIAgentManager()

        # Get the tools list
        tools = ai_manager.get_tools_list()
        print(f"Number of tools available: {len(tools)}")

        print("Attempting to process message with tools...")

        # Test with a message that would trigger tool usage (like creating a task)
        result = await ai_manager.process_message(
            user_id="1",
            message="Please create a task called 'Test AI Task' with description 'Created by AI'",
            conversation_history=[]
        )

        print("SUCCESS: AI Manager processed message with tools!")
        print(f"Result type: {result['type']}")
        if result['type'] == 'tool_calls':
            print(f"Tool calls triggered: {len(result.get('tool_calls', []))}")
            for tool_call in result.get('tool_calls', []):
                print(f"  - Tool: {tool_call['function']['name']}")
                print(f"    Args: {tool_call['function']['arguments']}")
        print(f"Result content: {result.get('content', 'No content')}")

        return True

    except Exception as e:
        print(f"ERROR: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_ai_with_tools())