"""
AI Configuration for Todo AI Chatbot
This module handles OpenAI configuration and client setup
"""

import os
import sys

# Only use system environment variables, no .env fallback
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")


class AIConfig:
    @staticmethod
    def get_openai_client():
        from openai import OpenAI

        if not OPENAI_API_KEY:
            print("ERROR: OPENAI_API_KEY not found in system environment variables!", file=sys.stderr)
            raise ValueError("OPENAI_API_KEY environment variable is required")

        client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
        )
        return client

    @staticmethod
    def get_async_openai_client():
        from openai import AsyncOpenAI

        if not OPENAI_API_KEY:
            print("ERROR: OPENAI_API_KEY not found in system environment variables!", file=sys.stderr)
            raise ValueError("OPENAI_API_KEY environment variable is required")

        client = AsyncOpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
        )
        return client

    @staticmethod
    def get_default_model():
        return OPENAI_MODEL