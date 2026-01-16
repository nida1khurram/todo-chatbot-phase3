#!/usr/bin/env python3
"""
Script to run the MCP (Model Context Protocol) server for the Todo AI Chatbot
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from mcp.server import Server
from mcp.types import TextContent
from sqlmodel import create_engine, Session
from src.models import Base, Task
from src.mcp_server.server import TodoMCPTools
from src.mcp_server.tools import get_mcp_tools_definitions
from src.settings import settings


# Create database engine and session using the same approach as the main app
if settings.database_url:
    DATABASE_URL = settings.database_url
else:
    DATABASE_URL = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

if DATABASE_URL.startswith("sqlite"):
    # SQLite-specific engine configuration
    engine = create_engine(
        DATABASE_URL,
        echo=settings.db_echo,
        connect_args={"check_same_thread": False}  # Required for SQLite with threading
    )
else:
    # PostgreSQL-specific engine configuration
    engine = create_engine(
        DATABASE_URL,
        echo=settings.db_echo,  # Set to True to see SQL queries in logs
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,  # Recycle connections after 5 minutes
    )

SessionLocal = Session


def create_db_and_tables():
    """Create database tables if they don't exist"""
    Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(server: Server):
    """Lifespan context manager for the MCP server"""
    print("Starting MCP server...")
    create_db_and_tables()
    yield
    print("Shutting down MCP server...")


async def main():
    """Main function to run the MCP server"""
    print("Initializing Todo MCP Server...")

    # Create a database session
    db_session = SessionLocal(bind=engine)

    # Create MCP server instance
    server = Server("todo-mcp-server", version="1.0.0")

    # Create tools instance
    todo_tools = TodoMCPTools(db_session)

    # The MCP server should expose resources and prompts for AI agents
    # The actual tools are handled by the AI agent layer
    @server.list_resources
    async def list_resources(context: dict):
        """List available resources"""
        return []

    @server.read_resource
    async def read_resource(uri: str, context: dict):
        """Read a specific resource"""
        return TextContent(type="text", text="Resource not found")

    @server.list_prompts
    async def list_prompts(context: dict):
        """List available prompts"""
        return []

    # Start the server
    print("Starting MCP server on localhost:8001...")
    async with server.serve(lifespan=lifespan, host="127.0.0.1", port=8001):
        print("MCP server is running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour, then repeat


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMCP server stopped by user.")
    except Exception as e:
        print(f"Error running MCP server: {e}")
        import traceback
        traceback.print_exc()