"""
Chat API for Todo AI Chatbot
This module provides API endpoints for chat functionality
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List, Optional, Dict, Any
from ..database import get_session
from ..models.user import User
from ..middleware.auth import get_current_user
from ..schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from ..services.chat_service import ChatService
from ..services.ai_agent_manager import AIAgentManager
from ..mcp_server.server import TodoMCPTools
import json

logger = logging.getLogger(__name__)

router = APIRouter()


async def execute_tool_calls(tool_calls: List[Dict[str, Any]], current_user: User, session: Session) -> str:
    """
    Execute the tool calls with authenticated user context
    """
    results = []

    # Create the tools instance with the authenticated user context
    tools = TodoMCPTools(db_session=session)

    for tool_call in tool_calls:
        function_name = tool_call["function"]["name"]
        arguments = tool_call["function"]["arguments"]

        # Override the user_id in the arguments with the authenticated user's ID
        arguments["user_id"] = str(current_user.id)

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
            logger.error(f"Error executing tool {function_name}: {str(e)}")
            results.append(f"Error executing {function_name}: {str(e)}")

    return "; ".join(results)


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Chat endpoint that processes user messages and returns AI responses.
    This endpoint is stateless - all conversation state is persisted to the database.
    """
    logger.info(f"User {current_user.id} sending chat message")

    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.id) != user_id:
        logger.warning(f"User {current_user.id} attempted to access chat for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        # Initialize services
        chat_service = ChatService(session)
        ai_agent_manager = AIAgentManager()

        # Get or create conversation
        conversation = chat_service.get_or_create_conversation(chat_request.conversation_id, current_user.id)

        # Add user message to conversation
        user_message = chat_service.add_message(
            conversation_id=conversation.id,
            user_id=current_user.id,
            role="user",
            content=chat_request.message
        )

        # Get conversation history for context
        history_messages = chat_service.get_conversation_history(conversation.id, current_user.id)

        # Format history for AI agent (convert to the format expected by the AI)
        formatted_history = []
        for msg in history_messages:
            formatted_history.append({
                "role": msg.role,
                "content": msg.content
            })

        # Process message with AI agent
        ai_result = await ai_agent_manager.process_message(
            user_id=str(current_user.id),
            message=chat_request.message,
            conversation_history=formatted_history[:-1]  # Exclude the current message we just added
        )

        # Extract AI response
        response_content = ""
        tool_calls = []

        if ai_result["type"] == "tool_calls":
            tool_calls = ai_result.get("tool_calls", [])

            # Execute the tool calls with authenticated user context
            tool_execution_result = await execute_tool_calls(tool_calls, current_user, session)

            # Generate a user-friendly response based on tool execution
            response_content = f"I've processed your request. {tool_execution_result}"
        else:
            response_content = ai_result.get("content", "I'm here to help with your tasks!")

        # Add AI response to conversation
        ai_message = chat_service.add_message(
            conversation_id=conversation.id,
            user_id=current_user.id,  # This represents the assistant's user context
            role="assistant",
            content=response_content
        )

        # Update conversation timestamp
        chat_service.update_conversation_timestamp(conversation.id)

        logger.info(f"Chat response generated for conversation {conversation.id}")

        # Return the response without the tool calls since they've been executed
        return ChatResponse(
            conversation_id=conversation.id,
            response=response_content,
            tool_calls=[]  # Clear tool calls since they've been executed
        )

    except Exception as e:
        logger.error(f"Error processing chat request for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )


@router.get("/{user_id}/conversations/{conversation_id}/history", response_model=ChatHistoryResponse)
def get_conversation_history(
    user_id: str,
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get the history of a specific conversation.
    """
    logger.info(f"User {current_user.id} requesting conversation history {conversation_id}")

    # Verify that the user_id in the path matches the authenticated user
    if str(current_user.id) != user_id:
        logger.warning(f"User {current_user.id} attempted to access history for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        chat_service = ChatService(session)

        # Verify conversation belongs to user
        conversation = chat_service.get_conversation(conversation_id, current_user.id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Get messages
        messages = chat_service.get_conversation_history(conversation_id, current_user.id)

        return ChatHistoryResponse(
            messages=messages,
            conversation_id=conversation_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation history {conversation_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the conversation history"
        )