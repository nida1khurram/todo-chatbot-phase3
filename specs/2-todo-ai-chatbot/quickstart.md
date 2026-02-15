# Todo AI Chatbot Quickstart Guide

## Overview
This guide provides a quick introduction to implementing the Todo AI Chatbot feature with MCP (Model Context Protocol) server architecture.

## Prerequisites
- Python 3.13+ with uv package manager
- Node.js 18+ for frontend
- PostgreSQL (Neon account recommended)
- OpenRouter API key
- Basic understanding of FastAPI, Next.js, and SQLModel

## Architecture Components

### 1. MCP Server
The MCP server acts as an intermediary between the AI agent and your backend services, providing standardized tools for todo operations.

### 2. AI Agent Service
Handles natural language processing and coordinates with the MCP server to execute todo operations.

### 3. Stateless Chat Endpoint
Manages conversation state by persisting to the database rather than holding state in memory.

### 4. Frontend Chat Interface
Provides a conversational UI for interacting with the AI assistant.

## Implementation Steps

### Step 1: Set Up MCP Server
1. Install MCP SDK dependencies
2. Create MCP tools for add_task, list_tasks, complete_task, delete_task, update_task
3. Connect tools to your existing database services
4. Validate user isolation in each tool

Example MCP tool implementation:
```python
async def add_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
    user_id = params["user_id"]
    title = params["title"]

    # Validate user access
    if not self.auth_service.validate_user(user_id):
        raise ValueError(f"Invalid user: {user_id}")

    # Create task in database
    new_task = Task(user_id=user_id, title=title, completed=False)
    self.db_session.add(new_task)
    self.db_session.commit()

    return {
        "task_id": new_task.id,
        "status": "created",
        "title": new_task.title
    }
```

### Step 2: Extend Database Schema
Add Conversation and Message entities to your existing SQLModel schema:
```python
class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default=datetime.utcnow())

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default=datetime.utcnow())
```

### Step 3: Create AI Agent Service
Configure the OpenAI Agents SDK with OpenRouter and connect to your MCP tools:
```python
def get_mcp_tools_definitions():
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["user_id", "title"]
                }
            }
        },
        # ... other tools
    ]
```

### Step 4: Implement Chat Endpoint
Create a stateless endpoint that loads conversation history, processes with AI, and saves responses:
```python
@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify user access
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get or create conversation
    chat_service = ChatService(session)
    conversation = chat_service.get_or_create_conversation(
        chat_request.conversation_id, current_user.id
    )

    # Add user message to conversation
    chat_service.add_message(
        conversation_id=conversation.id,
        user_id=current_user.id,
        role="user",
        content=chat_request.message
    )

    # Process with AI agent
    ai_agent_manager = AIAgentManager()
    ai_result = await ai_agent_manager.process_message(
        user_id=str(current_user.id),
        message=chat_request.message,
        conversation_history=formatted_history
    )

    # Return response
    return ChatResponse(
        conversation_id=conversation.id,
        response=ai_result.get("content", ""),
        tool_calls=ai_result.get("tool_calls", [])
    )
```

### Step 5: Frontend Integration
Integrate OpenAI ChatKit with your existing authentication:
```typescript
export default function TodoChat({ userId }: TodoChatProps) {
  const { token } = useAuth(); // Get JWT token from existing auth

  const handleCreateMessage = async (input: string) => {
    const response = await fetch(`/api/${userId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`, // Include JWT token
      },
      body: JSON.stringify({
        message: input,
        conversation_id: localStorage.getItem(`chat_conversation_${userId}`) || null
      }),
    });

    return response.json();
  };

  return (
    <Chat
      // ... other props
      onCreateMessage={handleCreateMessage}
    />
  );
}
```

## Configuration

### Environment Variables
Add these to your backend `.env`:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4o
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8080
```

Add these to your frontend `.env.local`:
```
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_domain_key_from_openai
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing

### Unit Tests
Write tests for each MCP tool to ensure they properly validate user access and perform operations correctly.

### Integration Tests
Test the full flow from user input to AI response and database changes.

### User Isolation Tests
Verify that users cannot access other users' conversations or tasks.

## Security Considerations

1. **User Isolation**: Always validate that the authenticated user matches the user_id in the request
2. **Input Validation**: Sanitize all inputs to prevent injection attacks
3. **Rate Limiting**: Implement rate limits to prevent abuse
4. **Authentication**: Ensure all endpoints require valid JWT tokens
5. **Tool Validation**: Verify that MCP tools properly validate user access before performing operations

## Performance Tips

1. **Connection Pooling**: Use database connection pooling for MCP tools
2. **Caching**: Cache frequently accessed data where appropriate
3. **Pagination**: Limit conversation history to prevent large payloads
4. **Async Operations**: Use async/await for database operations and API calls

## Troubleshooting

### Common Issues
- MCP tools returning access errors: Verify user_id validation in each tool
- AI not recognizing tasks: Check that tool schemas match MCP server implementation
- Slow responses: Optimize database queries and consider caching

### Debugging Tips
- Enable detailed logging for MCP tool calls
- Monitor conversation state persistence
- Check that authentication tokens are properly passed between components