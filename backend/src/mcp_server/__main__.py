"""
Main entry point for the MCP (Model Context Protocol) server
Used when running: python -m src.mcp_server
"""

import asyncio
import logging
import os
from mcp.server import Server
from sqlmodel import create_engine, Session
from ..models import Base
from ..settings import settings
from .server import TodoMCPTools


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


def create_db_and_tables():
    """Create database tables if they don't exist"""
    Base.metadata.create_all(bind=engine)


async def main():
    """Main function to run the MCP server"""
    logger.info("Initializing Todo MCP Server...")

    # Determine port from environment variable or default to 8001
    mcp_port = int(os.getenv("MCP_SERVER_PORT", "8001"))
    logger.info(f"MCP Server port set to: {mcp_port}")

    # Create a database session
    db_session = Session(bind=engine)

    # Create tools instance
    todo_tools = TodoMCPTools(db_session)

    # Create MCP server instance
    server = Server("todo-mcp-server", version="1.0.0")

    # Store the tools in the server for external access
    server.todo_tools = todo_tools

    # Start the server with the correct port from environment
    logger.info(f"Starting MCP server on localhost:{mcp_port}...")

    # Try to start the server - the exact API depends on the MCP SDK version
    try:
        # Attempt to use the most common method
        if hasattr(Server, 'serve'):
            # This is a more standard way for newer MCP SDK versions
            async with server.serve(host="127.0.0.1", port=mcp_port):
                logger.info(f"MCP server is running on port {mcp_port}. Press Ctrl+C to stop.")
                while True:
                    await asyncio.sleep(3600)  # Sleep for an hour, then repeat
        else:
            # Fallback for older MCP SDK versions
            # This might not work depending on the exact MCP implementation
            logger.info(f"Starting server on port {mcp_port} - waiting for connections...")
            # Placeholder for actual server implementation
            while True:
                await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"MCP server error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nMCP server stopped by user.")
    except Exception as e:
        logger.error(f"Error running MCP server: {e}")
        import traceback
        traceback.print_exc()