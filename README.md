# Todo AI Chatbot (Phase III)

An AI-powered todo application with natural language interface built with FastAPI (backend), Next.js (frontend), and MCP (Model Context Protocol) server architecture. This application demonstrates modern full-stack development with AI integration, featuring JWT-based authentication, PostgreSQL database, and conversational AI for todo management.

## Features

- **AI-Powered Natural Language Interface**: Manage todos using conversational commands like "Add a task to buy groceries" or "Show me all pending tasks"
- **MCP Server Architecture**: Model Context Protocol server with standardized tools for task operations
- **Conversational Context Management**: Maintains conversation history and context across interactions
- **User Authentication**: Secure registration and login with JWT tokens using industry-standard practices
- **Multi-User Support**: Each user has their own private tasks with complete data isolation
- **CRUD Operations**: Create, read, update, and delete tasks through both traditional UI and AI commands
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Security**: CSRF protection, security headers, input validation, and SQL injection prevention
- **Performance**: Database indexing for optimized queries and efficient API responses
- **Error Handling**: Comprehensive error handling with user-friendly feedback and logging
- **API Documentation**: Built-in Swagger UI and Redoc for API exploration and testing

## Tech Stack

- **Backend**: FastAPI, SQLModel, PostgreSQL (via Neon), JWT authentication
- **Frontend**: Next.js 14+, React, TypeScript, Tailwind CSS
- **AI Integration**: OpenAI Agents SDK, OpenRouter, MCP (Model Context Protocol) Server
- **Database**: PostgreSQL (Neon) with SQLModel ORM for tasks, conversations, and messages
- **Authentication**: JWT tokens with secure session management
- **Styling**: Tailwind CSS with responsive design principles
- **Testing**: Pytest for backend, Jest for frontend
- **Code Quality**: Ruff, Black, and MyPy for Python; ESLint and Prettier for JavaScript/TypeScript

## Architecture

### Backend Structure
```
backend/
├── src/
│   ├── models/          # Database models (User, Task, Conversation, Message)
│   ├── schemas/         # Pydantic schemas for validation
│   ├── api/            # API route handlers
│   ├── services/       # Business logic
│   ├── mcp_server/     # MCP (Model Context Protocol) server with tools
│   ├── ai_agents/      # OpenAI Agents SDK integration
│   ├── middleware/     # Authentication and validation middleware
│   ├── database.py     # Database connection and session management
│   └── main.py         # Application entry point
├── alembic/            # Database migration scripts
├── tests/              # Backend test suite
├── pyproject.toml      # Python dependencies and configuration
├── .env.example        # Environment variable template
└── .ruff.toml          # Python linting configuration
```

### Frontend Structure
```
frontend/
├── src/
│   ├── app/            # Next.js App Router pages
│   ├── components/     # Reusable React components
│   ├── lib/            # Utilities and API clients
│   │   ├── api/        # API client functions
│   │   └── context/    # React context providers
│   └── middleware.ts   # Next.js middleware for auth
├── public/             # Static assets
├── package.json        # Node.js dependencies
├── tailwind.config.js  # Tailwind CSS configuration
└── .env.local.example  # Environment variable template
```

### Key Architecture Decisions

1. **Security-First Design**: All API endpoints are protected by JWT authentication middleware with proper user isolation
2. **MCP Server Architecture**: Standardized tools for AI agents to perform task operations securely and efficiently
3. **Conversational Context Management**: State management for maintaining conversation history and context
4. **Database Optimization**: Strategic indexing on frequently queried fields (user_id, created_at, completed status)
5. **Performance**: Optimistic updates in the frontend for responsive user experience
6. **Error Handling**: Comprehensive error handling with user-friendly messages and proper logging
7. **Data Validation**: Multi-layer validation at API, service, and database levels

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get JWT token

### Tasks
- `GET /tasks` - Get all tasks for the authenticated user
- `POST /tasks` - Create a new task
- `GET /tasks/{task_id}` - Get a specific task
- `PUT /tasks/{task_id}` - Update a specific task
- `DELETE /tasks/{task_id}` - Delete a specific task

### AI Chat
- `POST /api/{user_id}/chat` - Send a message to the AI chatbot and receive a response
- `GET /api/{user_id}/conversations` - Get list of user's conversations
- `GET /api/{user_id}/conversations/{conversation_id}` - Get messages in a specific conversation

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **User Isolation**: Users can only access their own tasks
- **Input Validation**: Comprehensive validation for all inputs
- **Security Headers**: X-Content-Type-Options, X-Frame-Options, etc.
- **CSRF Protection**: Protection against Cross-Site Request Forgery
- **SQL Injection Prevention**: ORM-based queries prevent injection

## Performance Optimizations

- **Database Indexing**: Optimized queries with proper indexing
- **Caching**: JWT token validation caching
- **Optimized Queries**: Efficient database queries with proper relationships

## Setup Instructions

### Prerequisites
- Python 3.13+
- Node.js 18+
- PostgreSQL (or Neon account)
- OpenAI API key or OpenRouter API key

### Backend Setup
1. Navigate to the backend directory: `cd backend`
2. Install dependencies: `uv pip install -r requirements.txt` (or use poetry/pip)
3. Set up environment variables in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/todo_db
   SECRET_KEY=your-super-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
4. Run database migrations: `python -m alembic upgrade head`
5. Start the server: `uvicorn src.main:app --reload`

### Frontend Setup
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Set up environment variables in `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
4. Start the development server: `npm run dev`

## Environment Variables

### Backend
- `DATABASE_URL` - PostgreSQL database URL
- `SECRET_KEY` - Secret key for JWT tokens
- `ALGORITHM` - Algorithm for JWT encoding (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time (default: 30)
- `OPENAI_API_KEY` - OpenAI API key or OpenRouter API key for AI integration
- `OPENROUTER_API_KEY` - API key for OpenRouter (alternative to OpenAI)
- `MCP_SERVER_PORT` - Port for the MCP server (default: 8001)

### Frontend
- `NEXT_PUBLIC_API_URL` - Backend API URL

## Running the Application

1. Start the MCP server: `python -m src.mcp_server` (runs on port 8001 by default)
2. Start the backend server: `uvicorn src.main:app --reload` (runs on port 8000 by default)
3. Start the frontend server: `npm run dev` (runs on port 3000 by default)
4. Access the application at `http://localhost:3000`

## API Testing

You can test the API endpoints using:
- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`

## Error Handling

The application provides comprehensive error handling:
- Input validation errors with specific messages
- Authentication errors
- Database operation errors
- Network errors with fallbacks

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
