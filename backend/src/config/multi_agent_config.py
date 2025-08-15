"""
Configuration for the multi-agent system.
"""

import os
from typing import Dict, Any

class MultiAgentConfig:
    """Configuration class for multi-agent system."""
    
    # Agent configuration
    AGENTS_ENABLED = {
        "organic_farming": True,
        "financial": True, 
        "weather": True,
        "general": True
    }
    
    # Routing configuration
    ENABLE_PARALLEL_PROCESSING = True
    MAX_PARALLEL_AGENTS = 3
    
    # LLM configuration
    DEFAULT_MODEL = os.getenv("LLM_DEFAULT_MODEL", "gpt-3.5-turbo")
    TEMPERATURE = 0.7
    MAX_TOKENS = 2000
    
    # Response configuration
    STREAMING_DELAY = 0.03  # seconds between word chunks
    MAX_CONVERSATION_HISTORY = 10
    
    # Environment-based overrides
    USE_MULTI_AGENT = os.getenv("USE_MULTI_AGENT", "true").lower() == "true"
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get the complete configuration as a dictionary."""
        return {
            "agents_enabled": cls.AGENTS_ENABLED,
            "enable_parallel_processing": cls.ENABLE_PARALLEL_PROCESSING,
            "max_parallel_agents": cls.MAX_PARALLEL_AGENTS,
            "default_model": cls.DEFAULT_MODEL,
            "temperature": cls.TEMPERATURE,
            "max_tokens": cls.MAX_TOKENS,
            "streaming_delay": cls.STREAMING_DELAY,
            "max_conversation_history": cls.MAX_CONVERSATION_HISTORY,
            "use_multi_agent": cls.USE_MULTI_AGENT,
            "api_key_configured": bool(cls.LLM_API_KEY)
        }
    
    @classmethod
    def is_agent_enabled(cls, agent_name: str) -> bool:
        """Check if a specific agent is enabled."""
        return cls.AGENTS_ENABLED.get(agent_name, False)
    
    @classmethod
    def validate_config(cls) -> Dict[str, str]:
        """Validate the configuration and return any issues."""
        issues = []
        
        if not cls.LLM_API_KEY:
            issues.append("LLM_API_KEY not configured")
        
        if not any(cls.AGENTS_ENABLED.values()):
            issues.append("No agents are enabled")
        
        if cls.MAX_PARALLEL_AGENTS < 1:
            issues.append("MAX_PARALLEL_AGENTS must be at least 1")
        
        return issues