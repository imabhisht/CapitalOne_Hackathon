"""
Agricultural AI Advisor - Main Module

This module provides an intelligent agricultural advisory system using:
- LangGraph for agentic workflows
- Gemini LLM for natural language processing
- Exa.AI for agricultural knowledge search
- Weather API for environmental data
- MongoDB for chat history storage
"""

from .config import Config
from .database import chat_storage
from .llm_client import gemini_client
from .agent import agricultural_system
from .chat_service import agricultural_chat_service, generate_streaming_response, generate_complete_response, create_session

__all__ = [
    "Config",
    "chat_storage", 
    "gemini_client",
    "agricultural_system",
    "agricultural_chat_service",
    "generate_streaming_response",
    "generate_complete_response", 
    "create_session"
]

# Validate configuration on import
Config.validate_config() 