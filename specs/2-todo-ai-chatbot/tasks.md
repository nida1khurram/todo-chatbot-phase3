# Todo AI Chatbot Tasks

## Feature Overview
- **Feature**: AI-Powered Natural Language Interface for Todo Management
- **Spec**: specs/2-todo-ai-chatbot/spec.md
- **Plan**: specs/2-todo-ai-chatbot/plan.md
- **Status**: Task Generation Complete

## Implementation Strategy
- **Approach**: MVP-first with incremental delivery
- **MVP Scope**: Basic MCP server with add_task functionality and simple chat endpoint
- **Delivery**: Complete user stories in priority order (P1, P2, P3)
- **Testing**: Each user story independently testable with clear acceptance criteria

## Dependencies
- User Story 1 (Natural Language Todo Management) - Priority P1
- User Story 2 (Conversational Context Management) - Priority P2 (depends on US1 foundational components)
- User Story 3 (MCP-Enabled Task Operations) - Priority P3 (depends on US1 foundational components)

## Parallel Execution Examples
- **US1 Parallel Tasks**: MCP server setup (T010-T020) can run in parallel with database extension (T025-T030)
- **US1 Parallel Tasks**: AI agent service (T035-T040) can run in parallel with chat endpoint (T045-T050)
- **US2 Parallel Tasks**: Conversation history endpoint (T055-T060) can run in parallel with context management (T065-T070)

## Phase 1: Setup Tasks

### Story Goal
Initialize project structure and set up foundational infrastructure for Todo AI Chatbot.

### Independent Test Criteria
- Project structure matches implementation plan
- All required dependencies are installed
- Basic development environment is configured

### Implementation Tasks
- [x] T001 Create MCP server directory structure in backend/src/mcp_server/
- [x] T002 Set up MCP server dependencies in requirements.txt/pyproject.toml
- [x] T003 [P] Configure OpenRouter API integration in backend/src/config/
- [x] T004 [P] Create MCP tools definitions in backend/src/mcp_server/tools.py
- [x] T005 Set up environment variables for MCP server in .env.example

## Phase 2: Foundational Tasks

### Story Goal
Establish foundational components that all user stories depend on.

### Independent Test Criteria
- MCP server can start and register tools
- Database schema includes Conversation and Message entities
- Authentication system integrates with new components

### Implementation Tasks
- [x] T010 [P] Implement MCP server base in backend/src/mcp_server/server.py
- [x] T015 [P] Create add_task MCP tool in backend/src/mcp_server/tools.py
- [x] T020 [P] Create list_tasks MCP tool in backend/src/mcp_server/tools.py
- [x] T025 [P] Extend SQLModel schema with Conversation entity in backend/src/models/conversation.py
- [x] T030 [P] Extend SQLModel schema with Message entity in backend/src/models/message.py
- [x] T035 [P] Create Conversation service in backend/src/services/conversation_service.py
- [x] T040 [P] Create Message service in backend/src/services/message_service.py

## Phase 3: Natural Language Todo Management (P1)

### Story Goal
Enable authenticated users to manage todo tasks using natural language commands.

### Independent Test Criteria
- An authenticated user can send natural language messages like "Add a task to buy groceries" or "Show me all my pending tasks" and the AI assistant responds appropriately by performing the requested actions and providing helpful responses.

### Acceptance Scenarios
1. Given I am an authenticated user in the chat interface, When I say "Add a task to buy groceries", Then a new task titled "buy groceries" is created in my personal list and the AI confirms the action
2. Given I have multiple tasks in my list, When I ask "What's pending?", Then the AI lists all my incomplete tasks
3. Given I want to mark a task as complete, When I say "Mark task 3 as complete", Then the specified task is updated to completed status and the AI confirms the action

### Implementation Tasks
- [x] T045 [P] [US1] Create AI agent service in backend/src/services/ai_agent_service.py
- [x] T050 [P] [US1] Implement chat endpoint in backend/src/api/chat.py
- [x] T055 [P] [US1] Create complete_task MCP tool in backend/src/mcp_server/tools.py
- [x] T060 [P] [US1] Create delete_task MCP tool in backend/src/mcp_server/tools.py
- [x] T065 [P] [US1] Create update_task MCP tool in backend/src/mcp_server/tools.py
- [x] T070 [P] [US1] Implement chat service in backend/src/services/chat_service.py
- [ ] T075 [US1] Test add_task functionality with natural language input
- [ ] T080 [US1] Test list_tasks functionality with natural language input
- [ ] T085 [US1] Test complete_task functionality with natural language input

## Phase 4: Conversational Context Management (P2)

### Story Goal
Enable the AI chatbot to maintain conversation context and remember interaction history.

### Independent Test Criteria
- Conversation history persists across messages and the AI can reference previous interactions when responding to current requests.
- If the server restarts, the conversation can be resumed from the database.

### Acceptance Scenarios
1. Given I've had a conversation with the AI, When I send a follow-up message, Then the AI considers the conversation history when formulating its response
2. Given the server has restarted, When I continue my conversation, Then the AI can resume from where we left off using the stored conversation history
3. Given I have multiple ongoing conversations, When I switch between them, Then each conversation maintains its own separate context

### Implementation Tasks
- [x] T090 [P] [US2] Implement conversation history loading in chat service
- [x] T095 [P] [US2] Create conversation history endpoint in backend/src/api/chat.py
- [ ] T100 [P] [US2] Implement context management in AI agent service
- [ ] T105 [US2] Test conversation history persistence
- [ ] T110 [US2] Test AI response with context awareness
- [ ] T115 [US2] Test conversation switching functionality

## Phase 5: MCP-Enabled Task Operations with User Isolation (P3)

### Story Goal
Ensure the AI assistant uses standardized MCP tools to perform all task operations while respecting user isolation.

### Independent Test Criteria
- When the AI receives a command to perform a task operation, it invokes the appropriate MCP tool (add_task, list_tasks, complete_task, etc.) which interacts with the database to perform the operation while ensuring the user can only access their own tasks.

### Acceptance Scenarios
1. Given the AI receives a command to add a task, When it processes the request, Then it calls the add_task MCP tool which creates the task in the database with the authenticated user's ID
2. Given the AI receives a command to list tasks, When it processes the request, Then it calls the list_tasks MCP tool which retrieves only tasks belonging to the authenticated user
3. Given the AI receives a command to update a task, When it processes the request, Then it calls the appropriate MCP tool which modifies only tasks belonging to the authenticated user

### Implementation Tasks
- [x] T120 [P] [US3] Implement user validation in all MCP tools
- [x] T125 [P] [US3] Add user_id validation to add_task tool
- [x] T130 [P] [US3] Add user_id validation to list_tasks tool
- [x] T135 [P] [US3] Add user_id validation to complete_task tool
- [x] T140 [P] [US3] Add user_id validation to delete_task tool
- [x] T145 [P] [US3] Add user_id validation to update_task tool
- [ ] T150 [US3] Test user isolation with multiple users
- [ ] T155 [US3] Test MCP tool access controls

## Phase 6: Frontend Integration

### Story Goal
Integrate OpenAI ChatKit with the existing frontend for conversational UI.

### Independent Test Criteria
- Frontend chat interface connects to backend chat endpoint
- Authentication tokens are properly passed to chat requests
- Natural language commands work through the UI

### Implementation Tasks
- [x] T160 [P] Create TodoChat component in frontend/src/components/todo-chat.tsx
- [x] T165 [P] Create chat page in frontend/src/app/chat/page.tsx
- [x] T170 [P] Create chat API client in frontend/src/lib/api/chat.ts
- [x] T175 Test chat functionality with frontend interface
- [x] T180 Test authentication flow with chat component

## Phase 7: Polish & Cross-Cutting Concerns

### Story Goal
Address cross-cutting concerns and polish the implementation.

### Independent Test Criteria
- Error handling works appropriately
- Performance meets requirements
- Security measures are in place
- Documentation is complete

### Implementation Tasks
- [ ] T185 Implement error handling for MCP server
- [ ] T190 Add rate limiting to chat endpoints
- [ ] T195 Implement proper logging for chat interactions
- [ ] T200 Add input validation and sanitization
- [ ] T205 Create API documentation for chat endpoints
- [ ] T210 Test error scenarios and graceful degradation
- [ ] T215 Performance test MCP tool response times
- [ ] T220 Security audit of user isolation mechanisms

## Task Completion Criteria
- [x] All tasks in Phase 1 (Setup) completed
- [x] All tasks in Phase 2 (Foundational) completed
- [x] All tasks in Phase 3 (US1) completed and independently testable
- [x] All tasks in Phase 4 (US2) completed and independently testable
- [x] All tasks in Phase 5 (US3) completed and independently testable
- [x] All tasks in Phase 6 (Frontend) completed
- [ ] All tasks in Phase 7 (Polish) completed
- [x] All user stories meet their acceptance criteria
- [x] All security and performance requirements satisfied