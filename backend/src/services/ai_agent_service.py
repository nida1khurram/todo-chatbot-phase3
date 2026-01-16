"""
AI Agent Service for Todo AI Chatbot
This module handles natural language processing and coordinates with MCP server
"""

from openai import AsyncOpenAI
from typing import Dict, List, Any
import json
from ..config.ai_config import AIConfig


class AIAgentService:
    def __init__(self):
        self.client = AIConfig.get_async_openai_client()
        self.model = AIConfig.get_default_model()

    def create_agent(self, tools: List[Dict[str, Any]]):
        """Create an AI agent with specified tools"""
        return {
            "model": self.model,
            "tools": tools
        }

    async def run_conversation(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run a conversation with the AI agent"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            return self._process_response(response)
        except Exception as e:
            raise Exception(f"AI agent error: {str(e)}")

    def _get_guest_tools(self, original_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return a modified tool list for guest users"""
        # For guest users, we return tools that will provide informative responses
        # about the need to log in for task operations
        guest_tools = []
        for tool in original_tools:
            # Create a version of each tool that explains it requires authentication
            guest_tool = tool.copy()
            # Modify the tool to return a message about authentication
            guest_tools.append(guest_tool)

        # We'll add a special tool that handles guest user messages
        guest_tools.append({
            "type": "function",
            "function": {
                "name": "explain_guest_limitations",
                "description": "Explain to guest users that task operations require authentication",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "The operation the user wanted to perform"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Explanation of what the user needs to do"
                        }
                    },
                    "required": ["operation", "explanation"]
                }
            }
        })

        return guest_tools

    def _process_response(self, response):
        """Process the AI response and extract relevant information"""
        choice = response.choices[0]

        # Check if there are tool calls
        if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
            # Handle the case where there might be both tool calls and content
            content = choice.message.content or ""
            # If content is None, provide a default message
            if content is None:
                content = "Processing your request with tools..."

            return {
                "type": "tool_calls",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": json.loads(tool_call.function.arguments)
                        }
                    }
                    for tool_call in choice.message.tool_calls
                ],
                "content": content
            }
        else:
            content = choice.message.content or ""
            return {
                "type": "message",
                "content": content
            }