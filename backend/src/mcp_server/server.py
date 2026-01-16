"""
MCP Server Implementation for Todo AI Chatbot
This module implements the Model Context Protocol server with Official MCP SDK
"""

from mcp.server import Server
from mcp.types import TextContent
import asyncio
import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..models.task import Task


class MockAuthService:
    """Mock authentication service for testing user validation"""

    def validate_user(self, user_id: str) -> bool:
        """Validate if user exists and is authorized"""
        try:
            user_id_int = int(user_id)
            return user_id_int > 0  # Simple validation - user_id should be positive integer
        except ValueError:
            return False


class TodoMCPTools:
    def __init__(self, db_session: Session, auth_service=None):
        self.db_session = db_session
        self.auth_service = auth_service or MockAuthService()

    async def add_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """MCP tool to add a new task"""
        user_id = params["user_id"]
        title = params["title"]
        description = params.get("description", "")

        # Validate user access
        if not self.auth_service.validate_user(user_id):
            raise ValueError(f"Invalid user: {user_id}")

        # Convert user_id to integer for database storage
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise ValueError(f"Invalid user_id format: {user_id}")

        # Create task in database
        new_task = Task(user_id=user_id_int, title=title, description=description, completed=False)
        self.db_session.add(new_task)
        self.db_session.commit()
        self.db_session.refresh(new_task)

        return {
            "task_id": new_task.id,
            "status": "created",
            "title": new_task.title,
            "description": new_task.description,
            "completed": new_task.completed
        }

    async def list_tasks(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """MCP tool to list tasks"""
        user_id = params["user_id"]
        status_filter = params.get("status", "all")  # "all", "pending", "completed"

        # Validate user access
        if not self.auth_service.validate_user(user_id):
            raise ValueError(f"Invalid user: {user_id}")

        # Convert user_id to integer for database query
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise ValueError(f"Invalid user_id format: {user_id}")

        # Query tasks from database
        query = self.db_session.query(Task).filter(Task.user_id == user_id_int)

        if status_filter == "pending":
            query = query.filter(Task.completed == False)
        elif status_filter == "completed":
            query = query.filter(Task.completed == True)

        tasks = query.all()

        return [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "user_id": task.user_id
            }
            for task in tasks
        ]

    async def complete_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """MCP tool to mark a task as complete"""
        user_id = params["user_id"]
        task_id = params["task_id"]

        # Validate user access
        if not self.auth_service.validate_user(user_id):
            raise ValueError(f"Invalid user: {user_id}")

        # Convert IDs to integers for database operations
        try:
            user_id_int = int(user_id)
            task_id_int = int(task_id)
        except ValueError:
            raise ValueError(f"Invalid user_id or task_id format")

        # Find the task and verify it belongs to the user
        task = self.db_session.query(Task).filter(
            Task.id == task_id_int,
            Task.user_id == user_id_int
        ).first()

        if not task:
            raise ValueError(f"Task {task_id} not found for user {user_id}")

        # Update task completion status
        task.completed = True
        self.db_session.commit()
        self.db_session.refresh(task)

        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title
        }

    async def delete_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """MCP tool to remove a task from the list"""
        user_id = params["user_id"]

        # Handle both task_id and title-based deletion
        task_id = params.get("task_id")
        # Check for various possible parameter names that AI might use
        task_title = params.get("title") or params.get("task_name") or params.get("name") or params.get("task_title")

        # Validate user access
        if not self.auth_service.validate_user(user_id):
            raise ValueError(f"Invalid user: {user_id}")

        # Convert user_id to integer for database operations
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise ValueError(f"Invalid user_id format")

        task = None

        # If task_id is provided, use that
        if task_id is not None:
            try:
                task_id_int = int(task_id)
                # Find the task by ID and verify it belongs to the user
                task = self.db_session.query(Task).filter(
                    Task.id == task_id_int,
                    Task.user_id == user_id_int
                ).first()
            except ValueError:
                raise ValueError(f"Invalid task_id format")
        # If title is provided, find the task by title
        elif task_title is not None:
            # Escape special characters to prevent SQL issues
            escaped_title = task_title.replace('%', '\\%').replace('_', '\\_')
            task = self.db_session.query(Task).filter(
                Task.title.ilike(f"%{escaped_title}%"),  # Case-insensitive partial match
                Task.user_id == user_id_int
            ).first()
        else:
            raise ValueError("Either task_id or title must be provided for deletion")

        if not task:
            if task_id is not None:
                raise ValueError(f"Task {task_id} not found for user {user_id}")
            else:
                raise ValueError(f"Task with title '{task_title}' not found for user {user_id}")

        # Delete the task
        self.db_session.delete(task)
        self.db_session.commit()

        return {
            "task_id": task.id,
            "title": task.title,
            "status": "deleted"
        }

    async def update_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """MCP tool to modify task title or description"""
        user_id = params["user_id"]

        # Handle both task_id and title-based updates
        task_id = params.get("task_id")
        # Check for various possible parameter names that AI might use to identify the task to update
        task_title = (params.get("title_to_find") or
                     params.get("task_name") or
                     params.get("name") or
                     params.get("task_title") or
                     params.get("title"))  # "title" might be used to identify which task to update
        new_title = params.get("new_title") or params.get("title")  # "title" might be the new title
        new_description = params.get("new_description") or params.get("description")  # "description" might be the new description

        # Validate user access
        if not self.auth_service.validate_user(user_id):
            raise ValueError(f"Invalid user: {user_id}")

        # Convert user_id to integer for database operations
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise ValueError(f"Invalid user_id format")

        task = None

        # If task_id is provided, use that
        if task_id is not None:
            try:
                task_id_int = int(task_id)
                # Find the task by ID and verify it belongs to the user
                task = self.db_session.query(Task).filter(
                    Task.id == task_id_int,
                    Task.user_id == user_id_int
                ).first()
            except ValueError:
                raise ValueError(f"Invalid task_id format")
        # If title_to_find is provided, find the task by title
        elif task_title is not None:
            task = self.db_session.query(Task).filter(
                Task.title.ilike(f"%{task_title}%"),  # Case-insensitive partial match
                Task.user_id == user_id_int
            ).first()
        else:
            raise ValueError("Either task_id or title_to_find must be provided for update")

        if not task:
            if task_id is not None:
                raise ValueError(f"Task {task_id} not found for user {user_id}")
            else:
                raise ValueError(f"Task with title '{task_title}' not found for user {user_id}")

        # Update task properties if provided
        if new_title is not None:
            task.title = new_title
        if new_description is not None:
            task.description = new_description

        self.db_session.commit()
        self.db_session.refresh(task)

        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.title,
            "description": task.description
        }