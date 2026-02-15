"""
Test script to test the full chat flow (like the actual chat endpoint)
"""
import asyncio
from src.services.ai_agent_manager import AIAgentManager
from src.mcp_server.server import TodoMCPTools
from sqlmodel import create_engine, Session
from src.database import DATABASE_URL

# Create database engine and session for testing
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

async def execute_tool_calls(tool_calls, user_id, session):
    """
    Execute the tool calls with authenticated user context (same as chat endpoint)
    """
    results = []

    # Create the tools instance with the authenticated user context
    tools = TodoMCPTools(db_session=session)

    for tool_call in tool_calls:
        function_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]

        # Override the user_id in the arguments with the authenticated user's ID
        arguments["user_id"] = str(user_id)

        try:
            # Execute the appropriate tool function
            if function_name == "add_task":
                result = await tools.add_task(arguments)
                results.append(f"Added task: {result.get('title', 'Untitled')}")
            elif function_name == "list_tasks":
                result = await tools.list_tasks(arguments)
                results.append(f"Found {len(result)} tasks")
            elif function_name == "complete_task":
                result = await tools.complete_task(arguments)
                results.append(f"Completed task: {result.get('title', 'Untitled')}")
            elif function_name == "delete_task":
                result = await tools.delete_task(arguments)
                results.append(f"Deleted task ID: {result.get('task_id')}")
            elif function_name == "update_task":
                result = await tools.update_task(arguments)
                results.append(f"Updated task: {result.get('title', 'Untitled')}")
            else:
                results.append(f"Unknown function: {function_name}")

        except Exception as e:
            print(f"Error executing tool {function_name}: {str(e)}")
            results.append(f"Error executing {function_name}: {str(e)}")

    return "; ".join(results)

async def test_full_chat_flow():
    print("Testing full chat flow (like the actual chat endpoint)...")

    # Create a database session
    session = Session(bind=engine)

    try:
        # Create the AI agent manager
        ai_manager = AIAgentManager()

        print("Attempting to process message through full chat flow...")

        # Test with a message that would trigger tool usage
        ai_result = await ai_manager.process_message(
            user_id="1",
            message="Please create a task called 'Full Chat Test Task' with description 'Created by full chat flow'",
            conversation_history=[]
        )

        print(f"AI result type: {ai_result['type']}")

        if ai_result["type"] == "tool_calls":
            tool_calls = ai_result.get("tool_calls", [])
            print(f"Tool calls detected: {len(tool_calls)}")

            # Execute the tool calls with authenticated user context (like the chat endpoint does)
            tool_execution_result = await execute_tool_calls(tool_calls, "1", session)

            print(f"Tool execution result: {tool_execution_result}")
            response_content = f"I've processed your request. {tool_execution_result}"
        else:
            response_content = ai_result.get("content", "I'm here to help with your tasks!")

        print(f"Final response: {response_content}")

        session.close()
        return True

    except Exception as e:
        print(f"ERROR in full chat flow: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

        session.close()
        return False

if __name__ == "__main__":
    asyncio.run(test_full_chat_flow())