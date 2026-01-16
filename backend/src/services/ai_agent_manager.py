"""
AI Agent Manager for Todo AI Chatbot
This module manages the AI agent lifecycle and coordinates with MCP tools
"""

from .ai_agent_service import AIAgentService
from ..mcp_server.tools import get_mcp_tools_definitions
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class AIAgentManager:
    def __init__(self):
        self.ai_service = AIAgentService()
        self.tools = get_mcp_tools_definitions()

    async def process_message(self, user_id: str, message: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Process a user message and return AI response"""
        try:
            # Prepare messages for the AI
            messages = conversation_history + [{"role": "user", "content": message}]

            # Run the conversation with tools
            result = await self.ai_service.run_conversation(messages, self.tools)

            # Log the interaction
            logger.info(f"AI processed message for user {user_id}, result type: {result['type']}")

            return result
        except Exception as e:
            logger.error(f"Error processing message for user {user_id}: {str(e)}")
            return {
                "type": "error",
                "content": "Sorry, I encountered an error processing your request. Please try again."
            }

    def get_tools_list(self) -> List[Dict[str, Any]]:
        """Get the list of available tools"""
        return self.tools