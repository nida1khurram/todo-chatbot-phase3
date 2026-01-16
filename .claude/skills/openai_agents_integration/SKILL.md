# OpenAI Agents Integration Skill

## Description
Integrate OpenAI Agents SDK with OpenRouter as the LLM provider for AI-powered task management. Creates an intelligent agent that can understand natural language and perform todo operations using MCP tools.

## When to Use This Skill
- Creating AI agents for natural language todo management
- Integrating with OpenRouter as LLM provider
- Connecting AI agents to MCP tools for task operations
- Building conversational AI interfaces
- Implementing intelligent task processing

## Prerequisites
- OpenRouter API key configured
- MCP server with available tools
- Environment for running AI agents
- Proper error handling and rate limiting
- Database for conversation state management

## Implementation Steps

### 1. Install Dependencies
```bash
pip install openai openai-agents-sdk python-dotenv
# Note: Specific packages may vary based on OpenRouter requirements
```

### 2. Configure OpenRouter Settings
```python
# backend/src/ai_config.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o")

class AIConfig:
    @staticmethod
    def get_openrouter_client():
        from openai import OpenAI

        client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
        return client

    @staticmethod
    def get_default_model():
        return OPENROUTER_MODEL
```

### 3. Create AI Agent Service
```python
# backend/src/services/ai_agent_service.py
from openai import OpenAI
from typing import Dict, List, Any
import json
from .ai_config import AIConfig

class AIAgentService:
    def __init__(self):
        self.client = AIConfig.get_openrouter_client()
        self.model = AIConfig.get_default_model()

    def create_agent(self, tools: List[Dict[str, Any]]):
        """Create an AI agent with specified tools"""
        return {
            "model": self.model,
            "tools": tools
        }

    def run_conversation(self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Run a conversation with the AI agent"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            return self._process_response(response)
        except Exception as e:
            raise Exception(f"AI agent error: {str(e)}")

    def _process_response(self, response):
        """Process the AI response and extract relevant information"""
        choice = response.choices[0]

        # Check if there are tool calls
        if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
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
                "content": choice.message.content
            }
        else:
            return {
                "type": "message",
                "content": choice.message.content or ""
            }
```

### 4. Define MCP Tools Schema for OpenAI
```python
# backend/src/tools/mcp_tool_definitions.py
def get_mcp_tools_definitions():
    """Define tools that match MCP server capabilities for OpenAI"""
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user creating the task"
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the task"
                        },
                        "description": {
                            "type": "string",
                            "description": "The description of the task (optional)"
                        }
                    },
                    "required": ["user_id", "title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "Retrieve tasks from the list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user whose tasks to retrieve"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter tasks by status (optional, defaults to 'all')"
                        }
                    },
                    "required": ["user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as complete",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user"
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to mark as complete"
                        }
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Remove a task from the list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user"
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to delete"
                        }
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Modify task title or description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user"
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "The new title for the task (optional)"
                        },
                        "description": {
                            "type": "string",
                            "description": "The new description for the task (optional)"
                        }
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        }
    ]
```

### 5. Create AI Agent Manager
```python
# backend/src/services/ai_agent_manager.py
from .ai_agent_service import AIAgentService
from .mcp_tool_definitions import get_mcp_tools_definitions
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class AIAgentManager:
    def __init__(self):
        self.ai_service = AIAgentService()
        self.tools = get_mcp_tools_definitions()

    async def process_message(self, user_id: str, message: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Process a user message and return AI response"""
        try:
            # Prepare messages for the AI
            messages = conversation_history + [{"role": "user", "content": message}]

            # Run the conversation with tools
            result = self.ai_service.run_conversation(messages, self.tools)

            # Log the interaction
            logger.info(f"AI processed message for user {user_id}, result type: {result['type']}")

            return result
        except Exception as e:
            logger.error(f"Error processing message for user {user_id}: {str(e)}")
            return {
                "type": "error",
                "content": "Sorry, I encountered an error processing your request. Please try again."
            }

    def get_tools_list(self) -> List[Dict[str, Any]]:
        """Get the list of available tools"""
        return self.tools
```

### 6. Environment Configuration
```bash
# Add to your .env file
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4o
```

## Key Implementation Notes

### Tool Consistency
- Ensure MCP tools definitions match the actual MCP server implementation
- Keep parameter names and types consistent between OpenAI tools and MCP server
- Validate that return formats align between both systems

### Error Handling
- Handle API errors from OpenRouter gracefully
- Implement fallback responses when AI is unavailable
- Log errors for debugging and monitoring

### Security
- Validate user_id in all AI tool calls
- Implement rate limiting for AI requests
- Sanitize all inputs to prevent prompt injection

## Testing Strategy
```python
# backend/tests/test_ai_agent_service.py
import pytest
from unittest.mock import Mock, patch
from backend.src.services.ai_agent_service import AIAgentService

@pytest.fixture
def ai_service():
    with patch('backend.src.services.ai_config.AIConfig.get_openrouter_client') as mock_client:
        service = AIAgentService()
        service.client = mock_client
        return service

def test_run_conversation_with_tool_calls(ai_service):
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()
    mock_tool_call = Mock()

    mock_tool_call.function.name = "add_task"
    mock_tool_call.function.arguments = '{"user_id": "test", "title": "Test task"}'
    mock_tool_call.id = "call_123"

    mock_message.tool_calls = [mock_tool_call]
    mock_message.content = "I've added the task for you."

    mock_choice.message = mock_message
    mock_response.choices = [Mock()]
    mock_response.choices[0] = mock_choice

    ai_service.client.chat.completions.create.return_value = mock_response

    messages = [{"role": "user", "content": "Add a task to buy groceries"}]
    tools = [{"type": "function", "function": {"name": "add_task"}}]

    result = ai_service.run_conversation(messages, tools)

    assert result["type"] == "tool_calls"
    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["function"]["name"] == "add_task"
```

## Common Issues and Solutions

### Issue: OpenRouter API Configuration
**Problem**: OpenRouter API not responding correctly
**Solution**: Verify API key, model name, and endpoint URL are correct

### Issue: Tool Call Processing
**Problem**: AI generates tool calls that don't match expected format
**Solution**: Ensure tools definition schema is precise and matches MCP server expectations

### Issue: Context Window Limits
**Problem**: Long conversation histories exceed token limits
**Solution**: Implement conversation history truncation or summarization

## Success Criteria
- [ ] OpenAI agent successfully connects to OpenRouter
- [ ] AI correctly identifies when to use tools based on user input
- [ ] Tool calls are properly formatted and executable
- [ ] Error handling works for API failures
- [ ] Conversation context is maintained properly
- [ ] Integration with existing authentication system works

## Files Created
- `backend/src/ai_config.py` - AI configuration and client setup
- `backend/src/services/ai_agent_service.py` - Core AI agent functionality
- `backend/src/tools/mcp_tool_definitions.py` - Tool definitions for OpenAI
- `backend/src/services/ai_agent_manager.py` - High-level AI agent management
- `backend/tests/test_ai_agent_service.py` - Tests (optional)