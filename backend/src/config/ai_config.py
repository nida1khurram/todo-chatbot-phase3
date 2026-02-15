"""
AI Configuration for Todo AI Chatbot
This module handles OpenAI/OpenRouter configuration and client setup
"""

import os
import sys

# Check for OpenAI first (as specified by user), then fallback to OpenRouter
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# Use OpenAI as primary if available, otherwise use OpenRouter
if OPENAI_API_KEY:
    API_KEY = OPENAI_API_KEY
    BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
elif OPENROUTER_API_KEY:
    API_KEY = OPENROUTER_API_KEY
    BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
else:
    API_KEY = None
    BASE_URL = "https://api.openai.com/v1"  # Default
    MODEL = "gpt-3.5-turbo"  # Default


class AIConfig:
    @staticmethod
    def get_openai_client():
        from openai import OpenAI

        if not API_KEY:
            print("ERROR: No API key found (either OPENAI_API_KEY or OPENROUTER_API_KEY) in system environment variables!", file=sys.stderr)
            raise ValueError("Either OPENAI_API_KEY or OPENROUTER_API_KEY environment variable is required")

        client = OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL,
        )
        return client

    @staticmethod
    def get_async_openai_client():
        from openai import AsyncOpenAI

        if not API_KEY:
            print("ERROR: No API key found (either OPENAI_API_KEY or OPENROUTER_API_KEY) in system environment variables!", file=sys.stderr)
            raise ValueError("Either OPENAI_API_KEY or OPENROUTER_API_KEY environment variable is required")

        client = AsyncOpenAI(
            api_key=API_KEY,
            base_url=BASE_URL,
        )
        return client

    @staticmethod
    def get_default_model():
        return MODEL