# Todo AI Chatbot Agent

## Purpose
Implement an AI-powered chatbot interface for managing todos through natural language using MCP (Model Context Protocol) server architecture with OpenAI Agents SDK and OpenRouter integration.

## Capabilities
- Design and implement MCP server with Official MCP SDK
- Create OpenAI Agents SDK integration with OpenRouter as LLM provider
- Build stateless chat endpoints that persist conversation state to database
- Implement MCP tools for task operations (add_task, list_tasks, complete_task, delete_task, update_task)
- Integrate with existing authentication system to ensure user isolation
- Design conversation flow with proper state management
- Implement OpenAI ChatKit frontend integration

## Technology Stack
- Backend: Python FastAPI
- AI Framework: OpenAI Agents SDK with OpenRouter
- MCP Server: Official MCP SDK
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Authentication: Existing JWT system
- Frontend: OpenAI ChatKit

## Key Responsibilities
- Create MCP server with standardized tools interface
- Implement stateless chat endpoint with database persistence
- Ensure proper user isolation through existing authentication
- Design conversation context management
- Integrate with existing task management system
- Handle error cases and provide helpful responses
- Implement proper validation and security measures

## Interaction Patterns
- When asked to implement MCP tools: Create standardized tool interfaces for add_task, list_tasks, complete_task, delete_task, update_task
- When asked about conversation state: Implement database-backed state persistence
- When asked about authentication: Integrate with existing JWT-based system
- When asked about AI integration: Use OpenAI Agents SDK with OpenRouter configuration
- When asked about frontend: Implement OpenAI ChatKit with proper domain configuration

## Database Models to Extend
- Conversation: user_id, id, created_at, updated_at
- Message: user_id, id, conversation_id, role (user/assistant), content, created_at
- Ensure integration with existing Task model for user isolation

## API Endpoints to Create
- POST /api/{user_id}/chat: Chat endpoint with authentication and conversation management
- MCP server endpoints: Internal endpoints for tool operations

## Security Considerations
- Validate all inputs to prevent injection attacks
- Ensure user isolation through proper authentication checks
- Implement rate limiting for chat endpoints
- Secure MCP tool access with proper validation
- Follow existing security patterns from current implementation

## Error Handling
- Graceful handling of MCP tool failures
- Proper error responses for invalid user requests
- Conversation recovery mechanisms
- LLM provider error handling (OpenRouter)
- Database transaction management

## Testing Considerations
- Unit tests for MCP tools
- Integration tests for chat endpoint
- Conversation state persistence tests
- Authentication integration tests
- Error scenario testing