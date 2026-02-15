# Todo AI Chatbot Implementation Plan

## Feature Overview
- **Feature**: AI-Powered Natural Language Interface for Todo Management
- **Spec**: specs/2-todo-ai-chatbot/spec.md
- **Branch**: 2-todo-ai-chatbot
- **Status**: In Progress

## Technical Context

### Architecture Overview
- **Backend**: FastAPI with SQLModel ORM
- **Database**: PostgreSQL (Neon) with conversation/message entities
- **AI Framework**: OpenAI Agents SDK with OpenRouter as LLM provider
- **MCP Server**: Model Context Protocol server with Official MCP SDK
- **Frontend**: OpenAI ChatKit integration
- **Authentication**: JWT-based with existing user isolation

### Technology Stack
- **Languages**: Python (backend), TypeScript (frontend)
- **Frameworks**: FastAPI (backend), Next.js (frontend)
- **AI/ML**: OpenAI Agents SDK, OpenRouter API
- **Protocols**: MCP (Model Context Protocol)
- **Database**: PostgreSQL via SQLModel
- **Authentication**: JWT tokens with user isolation

### Known Requirements from Spec
- MCP tools for add_task, list_tasks, complete_task, delete_task, update_task
- Stateless chat endpoint with database-backed conversation persistence
- User isolation ensuring users only access their own data
- Natural language processing for todo management commands

## Constitution Check

### Alignment with Project Principles
- ✅ **Spec-Driven Development**: Following established spec-template structure
- ✅ **AI-First Design**: Prioritizing AI integration in todo management
- ✅ **Security-First**: Maintaining user isolation and authentication
- ✅ **Modularity**: Separating concerns with MCP server architecture
- ✅ **Scalability**: Stateless design for horizontal scaling

### Potential Violations
- **Performance**: MCP server introduces additional network hop - mitigate with proper caching and connection pooling

## Research Phase

### Required Research Areas

#### 1. MCP (Model Context Protocol) Implementation
- **Decision**: How to implement MCP server with Official MCP SDK
- **Rationale**: Spec requires MCP server with standardized tools for AI agents
- **Alternatives considered**:
  - Direct API calls vs MCP protocol
  - Self-hosted vs cloud MCP server
  - Different MCP SDK implementations

#### 2. OpenAI Agents SDK with OpenRouter Integration
- **Decision**: How to configure OpenAI Agents SDK to work with OpenRouter
- **Rationale**: Spec requires OpenAI Agents SDK with OpenRouter as LLM provider
- **Alternatives considered**:
  - Direct OpenAI API vs OpenRouter
  - Different agent architectures (function calling vs tools)

#### 3. Database Schema Extensions
- **Decision**: How to extend existing SQLModel schema with Conversation and Message entities
- **Rationale**: Need to store conversation history and messages persistently
- **Alternatives considered**:
  - Separate database vs extending existing schema
  - Different relationship models between entities

#### 4. Frontend Chat Integration
- **Decision**: How to integrate OpenAI ChatKit with existing frontend
- **Rationale**: Spec requires ChatKit for conversational UI
- **Alternatives considered**:
  - Custom chat UI vs ChatKit
  - Different chat UI libraries

## Data Model

### Extended Data Model

#### Conversation Entity
```python
class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default=datetime.utcnow())
    updated_at: datetime = Field(default=datetime.utcnow())

    # Relationships
    user: User = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")
```

#### Message Entity
```python
class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime = Field(default=datetime.utcnow())

    # Relationships
    user: User = Relationship(back_populates="messages")
    conversation: Conversation = Relationship(back_populates="messages")
```

#### Task Entity (Existing - with potential extensions)
```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = Field(default=datetime.utcnow())
    updated_at: datetime = Field(default=datetime.utcnow())

    # Relationships
    user: User = Relationship(back_populates="tasks")
```

## API Contracts

### Chat Endpoint Contract
```
POST /api/{user_id}/chat
Headers: Authorization: Bearer {jwt_token}
Request:
{
  "message": "string",
  "conversation_id": "integer" (optional)
}

Response:
{
  "conversation_id": "integer",
  "response": "string",
  "tool_calls": "array" (optional)
}
```

### Conversation History Endpoint Contract
```
GET /api/{user_id}/conversations/{conversation_id}/history
Headers: Authorization: Bearer {jwt_token}

Response:
{
  "messages": [
    {
      "id": "integer",
      "role": "string",
      "content": "string",
      "created_at": "datetime"
    }
  ],
  "conversation_id": "integer"
}
```

## MCP Tool Contracts

### add_task
- **Purpose**: Create a new task for the authenticated user
- **Input**:
```json
{
  "user_id": "string, required - from authenticated context",
  "title": "string, required - The title of the task",
  "description": "string, optional - The description of the task"
}
```
- **Output**:
```json
{
  "task_id": "integer - The ID of the created task",
  "status": "string - Status of the operation ('created')",
  "title": "string - The title of the created task"
}
```

### list_tasks
- **Purpose**: Retrieve tasks from the list for the authenticated user
- **Input**:
```json
{
  "user_id": "string, required - from authenticated context",
  "status": "string, optional - Filter by status ('all', 'pending', 'completed'), defaults to 'all'"
}
```
- **Output**:
```json
[
  {
    "id": "integer - The ID of the task",
    "title": "string - The title of the task",
    "completed": "boolean - Whether the task is completed"
  }
]
```

### complete_task
- **Purpose**: Mark a task as complete for the authenticated user
- **Input**:
```json
{
  "user_id": "string, required - from authenticated context",
  "task_id": "integer, required - The ID of the task to mark as complete"
}
```
- **Output**:
```json
{
  "task_id": "integer - The ID of the completed task",
  "status": "string - Status of the operation ('completed')",
  "title": "string - The title of the completed task"
}
```

### delete_task
- **Purpose**: Remove a task from the list for the authenticated user
- **Input**:
```json
{
  "user_id": "string, required - from authenticated context",
  "task_id": "integer, required - The ID of the task to delete"
}
```
- **Output**:
```json
{
  "task_id": "integer - The ID of the deleted task",
  "status": "string - Status of the operation ('deleted')",
  "title": "string - The title of the deleted task"
}
```

### update_task
- **Purpose**: Modify task title or description for the authenticated user
- **Input**:
```json
{
  "user_id": "string, required - from authenticated context",
  "task_id": "integer, required - The ID of the task to update",
  "title": "string, optional - The new title for the task",
  "description": "string, optional - The new description for the task"
}
```
- **Output**:
```json
{
  "task_id": "integer - The ID of the updated task",
  "status": "string - Status of the operation ('updated')",
  "title": "string - The updated title of the task"
}
```

## Implementation Approach

### Phase 1A: MCP Server Setup
1. Create MCP server module with Official MCP SDK
2. Implement add_task, list_tasks, complete_task, delete_task, update_task tools
3. Ensure tools validate user_id for proper isolation
4. Test tools independently

### Phase 1B: Database Extensions
1. Extend SQLModel schema with Conversation and Message models
2. Create Alembic migrations for new tables
3. Update existing services to work with extended schema
4. Implement conversation management services

### Phase 1C: AI Agent Integration
1. Configure OpenAI Agents SDK with OpenRouter
2. Define tool schemas that match MCP server capabilities
3. Create AI agent service to process natural language
4. Implement conversation context management

### Phase 1D: Chat Endpoint Implementation
1. Create stateless chat endpoint with conversation persistence
2. Integrate with AI agent service
3. Ensure proper authentication and user isolation
4. Implement error handling and validation

### Phase 1E: Frontend Integration
1. Integrate OpenAI ChatKit with existing Next.js app
2. Connect to backend chat endpoint
3. Implement proper authentication flow
4. Add usage examples and instructions

## Quickstart Guide

### Prerequisites
- Python 3.13+ with uv package manager
- Node.js 18+ for frontend
- PostgreSQL (Neon account recommended)
- OpenRouter API key
- Basic understanding of FastAPI, Next.js, and SQLModel

### Architecture Components

#### 1. MCP Server
The MCP server acts as an intermediary between the AI agent and your backend services, providing standardized tools for todo operations.

#### 2. AI Agent Service
Handles natural language processing and coordinates with the MCP server to execute todo operations.

#### 3. Stateless Chat Endpoint
Manages conversation state by persisting to the database rather than holding state in memory.

#### 4. Frontend Chat Interface
Provides a conversational UI for interacting with the AI assistant.

### Implementation Steps

#### Step 1: Set Up MCP Server
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

#### Step 2: Extend Database Schema
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

#### Step 3: Create AI Agent Service
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

#### Step 4: Implement Chat Endpoint
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

#### Step 5: Frontend Integration
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

## Risk Assessment

### High-Risk Areas
1. **MCP Server Integration**: New technology with potential compatibility issues
2. **AI Response Accuracy**: Natural language understanding may not be 100% accurate
3. **Security**: User isolation critical - must ensure no cross-user data access

### Mitigation Strategies
1. **Thorough Testing**: Unit tests for MCP tools, integration tests for AI responses
2. **Fallback Mechanisms**: Graceful degradation when AI doesn't understand requests
3. **Security Audits**: Code reviews and penetration testing for authentication

## Success Criteria Verification

### Measurable Outcomes from Spec
- [ ] Users can successfully add tasks using natural language commands with 95% success rate
- [ ] AI assistant correctly interprets and executes task operations from natural language with 90% accuracy
- [ ] Conversation state persists correctly across server restarts and maintains context
- [ ] All task operations are properly scoped to authenticated user (no cross-user access)
- [ ] MCP tools respond to requests with less than 2 second response time
- [ ] System correctly handles errors and provides helpful responses to users
- [ ] Chat interface maintains responsive performance with less than 3 second response time for AI interactions
- [ ] 95% of users can successfully complete the core task management workflow through natural language

## Next Steps

1. Begin with MCP server implementation as it's foundational for AI integration
2. Simultaneously work on database extensions for conversation persistence
3. Follow with AI agent configuration and testing
4. Complete with endpoint implementation and frontend integration