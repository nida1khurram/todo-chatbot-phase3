# Todo AI Chatbot (Phase III)Nida

An AI-powered todo application with natural language interface built with FastAPI (backend), Next.js (frontend), and MCP (Model Context Protocol) server architecture. This application demonstrates modern full-stack development with AI integration, featuring JWT-based authentication, PostgreSQL database, and conversational AI for todo management.

## Project Overview

This is the third phase of a progressive todo application development project, focusing on AI integration. The application allows users to manage their tasks through both traditional UI and natural language commands using AI agents.

## Development Phases

- **Phase I**: In-Memory Python Console App (completed)
- **Phase II**: Full-Stack Web Application with Authentication (completed)
- **Phase III**: AI-Powered Todo Chatbot (current phase) - *This phase*
- **Phase IV**: Local Kubernetes Deployment
- **Phase V**: Advanced Cloud Deployment

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

1. Start the backend server: `cd backend && uvicorn src.main:app --reload` (runs on port 8000 by default)
2. Start the frontend server: `cd frontend && npm run dev` (runs on port 3000 by default)
3. Access the application at `http://localhost:3000`

Note: The MCP server functionality may require additional configuration depending on your AI provider setup.

## Current Status

This project is currently in Phase III (AI-Powered Todo Chatbot). The application features:
- ✅ Complete backend API with user authentication and task management
- ✅ Full-featured frontend with Next.js and responsive design
- ✅ Database integration with PostgreSQL via SQLModel
- ✅ JWT-based authentication and user session management
- ⚠️ MCP (Model Context Protocol) server integration (may require configuration)

## Deployment

### Backend Deployment

The backend can be deployed to various platforms. Here are instructions for popular options:

#### Deploying to Hugging Face Spaces (Recommended for this project)

1. Create a Hugging Face account if you don't have one
2. Create a new Space with the "Docker" or "Gradio" runner
3. Add your API keys to Space Secrets:
   - `OPENAI_API_KEY`: Your OpenAI API key (or leave blank if using OpenRouter)
   - `OPENROUTER_API_KEY`: Your OpenRouter API key (or leave blank if using OpenAI)
   - `SECRET_KEY`: A strong, random secret key for JWT tokens
   - `DATABASE_URL`: PostgreSQL connection string
4. Clone this repository and modify the Dockerfile if needed
5. The backend will be accessible at `https://YOUR_USERNAME-hac2-chatbot.hf.space`

#### Deploying to Railway

1. Create a Railway account and link it to your GitHub
2. Create a new project and import this repository
3. Set the following environment variables in Railway:
   - `OPENAI_API_KEY`: Your OpenAI API key (or leave blank if using OpenRouter)
   - `OPENROUTER_API_KEY`: Your OpenRouter API key (or leave blank if using OpenAI)
   - `SECRET_KEY`: A strong, random secret key for JWT tokens
   - `DATABASE_URL`: PostgreSQL connection string
4. Deploy the project
5. The backend will be accessible at the Railway-generated URL

#### Deploying to Render

1. Create a Render account and connect your GitHub
2. Create a new Web Service and select this repository
3. Set the following environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key (or leave blank if using OpenRouter)
   - `OPENROUTER_API_KEY`: Your OpenRouter API key (or leave blank if using OpenAI)
   - `SECRET_KEY`: A strong, random secret key for JWT tokens
   - `DATABASE_URL`: PostgreSQL connection string
4. Set the build command to: `pip install -r requirements.txt`
5. Set the start command to: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
6. Deploy the service

### Frontend Deployment

#### Deploying to Vercel (Recommended)

1. Create a Vercel account and link it to your GitHub
2. Create a new project and import this repository
3. Set the following environment variable in Vercel:
   - `NEXT_PUBLIC_API_URL`: The URL of your deployed backend (e.g., `https://your-backend.onrender.com`)
4. The frontend will be accessible at the Vercel-generated URL

### Important Notes for Deployment

1. **CORS Configuration**: The backend is configured to allow requests from:
   - Local development: `http://localhost:3000`, `http://127.0.0.1:3000`, etc.
   - Vercel deployments: `https://*.vercel.app`
   - Hugging Face Spaces: `https://*.huggingface.co`, `https://*.hf.space`

2. **Environment Variables**: Make sure to set all required environment variables as secrets in your deployment platform rather than hardcoding them.

3. **Database**: Ensure your PostgreSQL database is accessible from your deployed backend.

4. **API Keys**: Never commit API keys to version control. Always use environment variables or platform-specific secrets management.

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
