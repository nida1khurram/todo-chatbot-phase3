# Phase III: Todo AI Chatbot Specification

**Feature**: AI-Powered Natural Language Interface for Todo Management
**Created**: 2026-01-09
**Status**: Draft
**Input**: User description: "Phase III: Todo AI Chatbot - Create an AI-powered chatbot interface for managing todos through natural language using MCP (Model Context Protocol) server architecture and using Claude Code and Spec-Kit Plus."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Todo Management (Priority: P1)

As an authenticated user, I want to manage my todo tasks using natural language commands so that I can interact with my todo list conversationally without clicking through UI elements.

**Why this priority**: This is the core functionality of the AI chatbot - enabling users to manage their tasks through natural language interaction.

**Independent Test**: An authenticated user can send natural language messages like "Add a task to buy groceries" or "Show me all my pending tasks" and the AI assistant responds appropriately by performing the requested actions and providing helpful responses.

**Acceptance Scenarios**:
1. **Given** I am an authenticated user in the chat interface, **When** I say "Add a task to buy groceries", **Then** a new task titled "buy groceries" is created in my personal list and the AI confirms the action
2. **Given** I have multiple tasks in my list, **When** I ask "What's pending?", **Then** the AI lists all my incomplete tasks
3. **Given** I want to mark a task as complete, **When** I say "Mark task 3 as complete", **Then** the specified task is updated to completed status and the AI confirms the action

---

### User Story 2 - Conversational Context Management (Priority: P1)

As an authenticated user, I want the AI chatbot to maintain conversation context and remember our interaction history so that I can have natural, flowing conversations about my tasks.

**Why this priority**: Context management is essential for a natural conversational experience - users expect the AI to remember what they've discussed previously.

**Independent Test**: The conversation history persists across messages and the AI can reference previous interactions when responding to current requests. If the server restarts, the conversation can be resumed from the database.

**Acceptance Scenarios**:
1. **Given** I've had a conversation with the AI, **When** I send a follow-up message, **Then** the AI considers the conversation history when formulating its response
2. **Given** the server has restarted, **When** I continue my conversation, **Then** the AI can resume from where we left off using the stored conversation history
3. **Given** I have multiple ongoing conversations, **When** I switch between them, **Then** each conversation maintains its own separate context

---

### User Story 3 - MCP-Enabled Task Operations with User Isolation (Priority: P1)

As an authenticated user, I want the AI assistant to use standardized MCP tools to perform all task operations while respecting user isolation so that the system remains scalable and stateless while maintaining secure access to my personal data.

**Why this priority**: MCP tools provide a standardized interface for the AI to interact with the application, ensuring proper user isolation and enabling proper separation of concerns and scalability.

**Independent Test**: When the AI receives a command to perform a task operation, it invokes the appropriate MCP tool (add_task, list_tasks, complete_task, etc.) which interacts with the database to perform the operation while ensuring the user can only access their own tasks.

**Acceptance Scenarios**:
1. **Given** the AI receives a command to add a task, **When** it processes the request, **Then** it calls the add_task MCP tool which creates the task in the database with the authenticated user's ID
2. **Given** the AI receives a command to list tasks, **When** it processes the request, **Then** it calls the list_tasks MCP tool which retrieves only tasks belonging to the authenticated user
3. **Given** the AI receives a command to update a task, **When** it processes the request, **Then** it calls the appropriate MCP tool which modifies only tasks belonging to the authenticated user

---

### Edge Cases

- What happens when a user asks about a task that doesn't exist? The AI should gracefully handle the error and inform the user.
- How does the system handle malformed natural language requests? The AI should ask for clarification or provide helpful guidance.
- What happens when the MCP server is temporarily unavailable? The system should provide appropriate error handling and retry mechanisms.
- How does the system handle concurrent conversations from the same user? Each conversation should maintain its own separate state and context.
- What happens when an unauthorized user tries to access the chat endpoint? The system should return 401 Unauthorized errors.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept natural language input from authenticated users via the chat endpoint
- **FR-002**: System MUST use OpenAI Agents SDK integrated with OpenRouter as the LLM provider for AI logic
- **FR-003**: System MUST implement an MCP server with Official MCP SDK that exposes task operations as tools
- **FR-004**: System MUST provide a stateless chat endpoint that persists conversation state to the database
- **FR-005**: System MUST support all Basic Level features through natural language commands (Add Task, Delete Task, Update Task, View Task List, Mark as Complete)
- **FR-006**: System MUST integrate with existing JWT token authentication system to ensure user isolation
- **FR-007**: System MUST ensure user isolation - users can only access their own tasks through the chat interface
- **FR-008**: System MUST store conversation history, messages, and tasks in Neon Serverless PostgreSQL using SQLModel
- **FR-009**: System MUST expose MCP tools for add_task, list_tasks, complete_task, delete_task, and update_task operations
- **FR-010**: System MUST handle errors gracefully and provide helpful responses to users
- **FR-011**: System MUST maintain conversation context across multiple exchanges
- **FR-012**: System MUST validate all inputs to prevent injection attacks and ensure data integrity
- **FR-013**: System MUST integrate OpenAI Agents SDK with OpenRouter using proper API keys and configuration

### MCP Tools Specification

#### Tool: add_task
- **Purpose**: Create a new task for the authenticated user
- **Parameters**: user_id (string, required - from authenticated context), title (string, required), description (string, optional)
- **Returns**: task_id, status, title
- **Example Input**: `{"user_id": "ziakhan", "title": "Buy groceries", "description": "Milk, eggs, bread"}`
- **Example Output**: `{"task_id": 5, "status": "created", "title": "Buy groceries"}`

#### Tool: list_tasks
- **Purpose**: Retrieve tasks from the list for the authenticated user
- **Parameters**: user_id (string, required - from authenticated context), status (string, optional: "all", "pending", "completed")
- **Returns**: Array of task objects belonging to the user
- **Example Input**: `{"user_id": "ziakhan", "status": "pending"}`
- **Example Output**: `[{"id": 1, "title": "Buy groceries", "completed": false}, ...]`

#### Tool: complete_task
- **Purpose**: Mark a task as complete for the authenticated user
- **Parameters**: user_id (string, required - from authenticated context), task_id (integer, required)
- **Returns**: task_id, status, title
- **Example Input**: `{"user_id": "ziakhan", "task_id": 3}`
- **Example Output**: `{"task_id": 3, "status": "completed", "title": "Call mom"}`

#### Tool: delete_task
- **Purpose**: Remove a task from the list for the authenticated user
- **Parameters**: user_id (string, required - from authenticated context), task_id (integer, required)
- **Returns**: task_id, status, title
- **Example Input**: `{"user_id": "ziakhan", "task_id": 2}`
- **Example Output**: `{"task_id": 2, "status": "deleted", "title": "Old task"}`

#### Tool: update_task
- **Purpose**: Modify task title or description for the authenticated user
- **Parameters**: user_id (string, required - from authenticated context), task_id (integer, required), title (string, optional), description (string, optional)
- **Returns**: task_id, status, title
- **Example Input**: `{"user_id": "ziakhan", "task_id": 1, "title": "Buy groceries and fruits"}`
- **Example Output**: `{"task_id": 1, "status": "updated", "title": "Buy groceries and fruits"}`

### Key Entities

- **Task**: Represents a todo item with user_id, id, title, description, completion status, and timestamps
- **Conversation**: Represents a chat session with user_id, id, and timestamps
- **Message**: Represents a chat message with user_id, id, conversation_id, role (user/assistant), content, and timestamp
- **MCP Tool**: Standardized interface for AI agents to perform operations on tasks

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully add tasks using natural language commands with 95% success rate
- **SC-002**: AI assistant correctly interprets and executes task operations from natural language with 90% accuracy
- **SC-003**: Conversation state persists correctly across server restarts and maintains context
- **SC-004**: All task operations are properly scoped to authenticated user (no cross-user access)
- **SC-005**: MCP tools respond to requests with less than 2 second response time
- **SC-006**: System correctly handles errors and provides helpful responses to users
- **SC-007**: Chat interface maintains responsive performance with less than 3 second response time for AI interactions
- **SC-008**: 95% of users can successfully complete the core task management workflow through natural language

### Technical Success Criteria

- **TSC-001**: Stateless architecture maintains conversation state in database without server-side persistence
- **TSC-002**: MCP server implements all required tools with proper error handling and validation
- **TSC-003**: Authentication system properly validates JWT tokens and enforces user isolation
- **TSC-004**: Database models correctly represent all required entities with proper relationships
- **TSC-005**: OpenAI Agents SDK integrates with OpenRouter and MCP tools seamlessly

## Natural Language Commands Mapping

| User Says | Agent Should |
|-----------|--------------|
| "Add a task to buy groceries" | Call add_task with title "Buy groceries" |
| "Show me all my tasks" | Call list_tasks with status "all" |
| "What's pending?" | Call list_tasks with status "pending" |
| "Mark task 3 as complete" | Call complete_task with task_id 3 |
| "Delete the meeting task" | Call list_tasks first, then delete_task |
| "Change task 1 to 'Call mom tonight'" | Call update_task with new title |
| "I need to remember to pay bills" | Call add_task with title "Pay bills" |
| "What have I completed?" | Call list_tasks with status "completed" |

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────────────────────────────────┐     ┌─────────────────┐
│                 │     │              FastAPI Server                   │     │                 │
│                 │     │  ┌────────────────────────────────────────┐  │     │                 │
│  ChatKit UI     │────▶│  │         Chat Endpoint                  │  │     │    Neon DB      │
│  (Frontend)     │     │  │  POST /api/{user_id}/chat             │  │     │  (PostgreSQL)   │
│                 │     │  └───────────────┬────────────────────────┘  │     │                 │
│                 │     │                  │                           │     │  - tasks        │
│                 │     │                  ▼                           │     │  - conversations │
│                 │     │  ┌────────────────────────────────────────┐  │────▶│  - messages     │
│                 │◀────│  │      OpenAI Agents SDK                 │  │     │                 │
│                 │     │  │      (Agent + Runner)                  │  │     │                 │
│                 │     │  └───────────────┬────────────────────────┘  │     │                 │
│                 │     │                  │                           │     │                 │
│                 │     │                  ▼                           │     │                 │
│                 │     │  ┌────────────────────────────────────────┐  │────▶│                 │
│                 │     │  │         MCP Server                     │  │     │                 │
│                 │     │  │  (MCP Tools for Task Operations)       │  │◀────│                 │
│                 │     │  └────────────────────────────────────────┘  │     │                 │
└─────────────────┘     └──────────────────────────────────────────────┘     └─────────────────┘
```

## Implementation Approach

1. **Database Layer**: Extend existing SQLModel models to include Conversation and Message entities alongside Task
2. **MCP Server**: Implement Official MCP SDK server with the five required tools (add_task, list_tasks, complete_task, delete_task, update_task) using the **mcp_server_setup** skill
3. **AI Integration**: Configure OpenAI Agents SDK to use OpenRouter as the LLM provider with MCP tools integration using the **openai_agents_integration** skill
4. **Chat Endpoint**: Create stateless FastAPI endpoint that loads conversation history, runs agent, and persists messages using the **stateless_chat_endpoint** skill
5. **Frontend**: Integrate OpenAI ChatKit with proper domain allowlist configuration using the **chatkit_integration** skill
6. **Authentication**: Integrate with existing JWT-based authentication system to ensure user isolation and leverage established security patterns
7. **OpenRouter Configuration**: Set up OpenRouter API integration with proper environment variables and model selection for the Agents SDK
8. **Agent Coordination**: Use the **todo-ai-chatbot-agent** to coordinate all components and ensure proper integration

## Available Agents and Skills for Implementation

### Agents

#### todo-ai-chatbot-agent
- **Purpose**: Implements the complete AI chatbot functionality with MCP server, OpenAI integration, and frontend components
- **Usage**: Use this agent when you want to implement the entire Phase 3 functionality at once or coordinate multiple components
- **Commands**:
  - "@todo-ai-chatbot-agent implement full chatbot system"
  - "@todo-ai-chatbot-agent create MCP server with tools"
  - "@todo-ai-chatbot-agent integrate OpenAI with OpenRouter"

### Skills

#### mcp_server_setup
- **Purpose**: Sets up the MCP (Model Context Protocol) server with Official MCP SDK
- **Usage**: Use this skill to create the MCP server that exposes task operations as standardized tools
- **Command**: "@mcp_server_setup create MCP server with add_task, list_tasks, complete_task, delete_task, update_task tools"

#### openai_agents_integration
- **Purpose**: Integrates OpenAI Agents SDK with OpenRouter as the LLM provider
- **Usage**: Use this skill to create the AI agent that understands natural language and uses MCP tools
- **Command**: "@openai_agents_integration configure OpenAI agent with OpenRouter for todo management"

#### chatkit_integration
- **Purpose**: Integrates OpenAI ChatKit for the frontend chat interface
- **Usage**: Use this skill to create the conversational UI that connects to your backend
- **Command**: "@chatkit_integration create chat component with authentication and domain configuration"

#### stateless_chat_endpoint
- **Purpose**: Creates a stateless chat endpoint with database persistence
- **Usage**: Use this skill to implement the backend API that handles chat requests and stores conversation history
- **Command**: "@stateless_chat_endpoint create chat API with conversation persistence and AI integration"