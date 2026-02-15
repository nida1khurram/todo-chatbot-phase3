"""
MCP Tools Definitions for Todo AI Chatbot
This module defines the tools that match MCP server capabilities for OpenAI
"""

def get_mcp_tools_definitions():
    """Define tools that match MCP server capabilities for OpenAI"""
    return [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Create a new task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user creating the task"
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the task"
                        },
                        "description": {
                            "type": "string",
                            "description": "The description of the task (optional)"
                        }
                    },
                    "required": ["user_id", "title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "Retrieve tasks from the list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user whose tasks to retrieve"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter tasks by status (optional, defaults to 'all')"
                        }
                    },
                    "required": ["user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as complete",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user"
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to mark as complete"
                        }
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Remove a task from the list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user"
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to delete (optional if title is provided)"
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the task to delete (optional if task_id is provided)"
                        }
                    },
                    "required": ["user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_task",
                "description": "Modify task title or description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The ID of the user"
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to update (optional if title_to_find is provided)"
                        },
                        "title_to_find": {
                            "type": "string",
                            "description": "The title of the task to update (optional if task_id is provided)"
                        },
                        "new_title": {
                            "type": "string",
                            "description": "The new title for the task (optional)"
                        },
                        "new_description": {
                            "type": "string",
                            "description": "The new description for the task (optional)"
                        }
                    },
                    "required": ["user_id"]
                }
            }
        }
    ]