# MCP Server Setup Skill

## Description
Set up an MCP (Model Context Protocol) server with Official MCP SDK that exposes task operations as standardized tools for AI agents. Creates a robust, scalable server that handles tool requests from AI agents and integrates with your backend systems.

## When to Use This Skill
- Creating MCP server infrastructure for AI agent integration
- Setting up standardized tool interfaces for AI operations
- Building stateless tool execution layer
- Integrating AI agents with existing backend systems
- Implementing Model Context Protocol for AI development

## Prerequisites
- Python 3.13+ project with proper structure
- Dependencies available for MCP SDK
- Existing backend services to connect to MCP tools
- Database connection for tool operations
- Authentication system for user isolation

## Implementation Steps

### 1. Install MCP Dependencies
```bash
pip install mcp
# Additional dependencies as needed for your specific tools
```

### 2. Create MCP Server Structure
```python
# backend/src/mcp_server/server.py
from mcp.server import Server
from mcp.types import TextContent
import asyncio
import json
from typing import List, Dict, Any

class TodoMCPTools:
    def __init__(self, db_session, auth_service):
        self.db_session = db_session
        self.auth_service = auth_service

    async def add_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """MCP tool to add a new task"""
        user_id = params["user_id"]
        title = params["title"]
        description = params.get("description", "")

        # Validate user access
        if not self.auth_service.validate_user(user_id):
            raise ValueError(f"Invalid user: {user_id}")

        # Create task in database
        from backend.src.models.task import Task
        new_task = Task(user_id=user_id, title=title, description=description, completed=False)
        self.db_session.add(new_task)
        self.db_session.commit()
        self.db_session.refresh(new_task)

        return {
            "task_id": new_task.id,
            "status": "created",
            "title": new_task.title
        }

    async def list_tasks(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """MCP tool to list tasks"""
        user_id = params["user_id"]
        status_filter = params.get("status", "all")  # "all", "pending", "completed"

        # Validate user access
        if not self.auth_service.validate_user(user_id):
            raise ValueError(f"Invalid user: {user_id}")

        # Query tasks from database
        from backend.src.models.task import Task
        query = self.db_session.query(Task).filter(Task.user_id == user_id)

        if status_filter == "pending":
            query = query.filter(Task.completed == False)
        elif status_filter == "completed":
            query = query.filter(Task.completed == True)

        tasks = query.all()

        return [
            {"id": task.id, "title": task.title, "completed": task.completed}
            for task in tasks
        ]

    # Similar implementations for complete_task, delete_task, update_task
```

### 3. Configure MCP Server
```python
# backend/src/mcp_server/__init__.py
from mcp.server import Server
from .server import TodoMCPTools
from backend.src.database import get_session
from backend.src.middleware.auth import get_current_user

def create_mcp_server():
    server = Server("todo-mcp-server")

    # Initialize tools with dependencies
    tools_instance = TodoMCPTools(
        db_session=get_session(),
        auth_service=None  # Inject your auth service
    )

    # Register tools with the server
    @server.tool("add_task")
    async def add_task_handler(params: Dict[str, Any]) -> Dict[str, Any]:
        return await tools_instance.add_task(params)

    @server.tool("list_tasks")
    async def list_tasks_handler(params: Dict[str, Any]) -> List[Dict[str, Any]]:
        return await tools_instance.list_tasks(params)

    # Add other tool handlers...

    return server
```

### 4. Create MCP Server Main Entry Point
```python
# backend/src/mcp_server/main.py
import asyncio
from . import create_mcp_server

async def main():
    server = create_mcp_server()

    # Start the server (usually connects to stdin/stdout for MCP protocol)
    async with server.serve_stdio():
        print("MCP server running...")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
```

### 5. Environment Configuration
```bash
# Add MCP-specific environment variables
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8080
MCP_DEBUG_MODE=true
```

## Key Implementation Notes

### Tool Parameters and Responses
Each MCP tool should follow the standardized format:
- Input: Dictionary with required and optional parameters
- Output: Dictionary with consistent response format
- Error handling: Proper exception raising for invalid inputs

### Security Considerations
- Validate user_id in all tools for proper isolation
- Implement rate limiting for tool calls
- Sanitize all inputs to prevent injection attacks
- Use proper database transactions

### Integration with Existing Systems
- Connect to existing database session management
- Integrate with existing authentication system
- Maintain consistency with existing data models
- Follow existing error handling patterns

## Testing Strategy
```python
# backend/tests/test_mcp_tools.py
import pytest
from unittest.mock import Mock
from backend.src.mcp_server.server import TodoMCPTools

@pytest.fixture
def mock_auth_service():
    auth_service = Mock()
    auth_service.validate_user.return_value = True
    return auth_service

@pytest.fixture
def tools_instance(mock_auth_service):
    db_session = Mock()
    return TodoMCPTools(db_session, mock_auth_service)

def test_add_task_success(tools_instance):
    params = {
        "user_id": "test_user",
        "title": "Test task",
        "description": "Test description"
    }

    result = tools_instance.add_task(params)

    assert result["status"] == "created"
    assert result["title"] == "Test task"
    # Additional assertions...
```

## Common Issues and Solutions

### Issue: MCP Protocol Compatibility
**Problem**: MCP client expects specific protocol format
**Solution**: Ensure proper MCP SDK implementation with correct message formatting

### Issue: Authentication Integration
**Problem**: MCP tools need to validate user access
**Solution**: Pass authentication service to tools instance and validate user_id in each tool

### Issue: Database Connection
**Problem**: MCP tools need database access
**Solution**: Use dependency injection to provide database session to tools

## Success Criteria
- [ ] MCP server starts successfully
- [ ] All tools respond to requests with proper format
- [ ] User isolation maintained through authentication
- [ ] Database operations work correctly
- [ ] Error handling implemented properly
- [ ] Tools accessible to AI agents via MCP protocol

## Files Created
- `backend/src/mcp_server/server.py` - MCP tools implementation
- `backend/src/mcp_server/__init__.py` - Server configuration
- `backend/src/mcp_server/main.py` - Entry point
- `backend/tests/test_mcp_tools.py` - Tests (optional)