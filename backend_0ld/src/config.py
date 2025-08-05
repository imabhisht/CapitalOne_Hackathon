import os
from typing import Optional

class Config:
    """Configuration settings for the Agricultural AI Advisor"""
    
    # LLM Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Weather API Configuration
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    WEATHER_BASE_URL: str = "http://api.weatherapi.com/v1"
    
    # Exa.AI Configuration
    EXA_API_KEY: str = os.getenv("EXA_API_KEY", "")
    EXA_BASE_URL: str = "https://api.exa.ai"
    
    # MongoDB Configuration
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = "agricultural_advisor"
    MONGODB_COLLECTION: str = "chat_history"
    
    # Application Settings
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.7
    STREAMING_DELAY: float = 0.1
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required API keys are set"""
        required_keys = [
            ("GEMINI_API_KEY", cls.GEMINI_API_KEY),
            ("WEATHER_API_KEY", cls.WEATHER_API_KEY),
            ("EXA_API_KEY", cls.EXA_API_KEY)
        ]
        
        missing_keys = [key for key, value in required_keys if not value]
        
        if missing_keys:
            print(f"Warning: Missing API keys: {', '.join(missing_keys)}")
            print("Please set these environment variables for full functionality.")
            return False
        
        return True 