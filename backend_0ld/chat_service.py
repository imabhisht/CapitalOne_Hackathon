import asyncio
from typing import AsyncGenerator, Tuple, Optional, Dict
import logging
import uuid
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the agricultural advisor system
from src.agent import agricultural_system
from src.config import Config

class ChatService:
    """Agricultural AI Advisor ChatService"""
    
    def __init__(self, delay: float = 0.1):
        self.delay = delay
        self.agricultural_system = agricultural_system
        logger.info("Agricultural advisor system initialized successfully")
    
    def _create_session_id(self) -> str:
        """Create a new session ID"""
        return str(uuid.uuid4())
    
    async def generate_streaming_response(
        self, 
        message: str, 
        **kwargs
    ) -> AsyncGenerator[Tuple[str, bool], None]:
        """
        Generate streaming response using agricultural advisor
        
        Args:
            message: User's input message
            **kwargs: Additional arguments including:
                - session_id: Optional session ID for conversation continuity
                - coordinates: Optional lat/lon coordinates for weather data
                
        Yields:
            Tuple[str, bool]: (content_chunk, is_complete)
        """
        try:
            # Use agricultural advisor system for all queries
            session_id = kwargs.get('session_id', self._create_session_id())
            coordinates = kwargs.get('coordinates', None)
            
            logger.info(f"Processing query with agricultural system, session: {session_id}")
            
            # Use the agricultural system for streaming response
            async for chunk, is_complete in self.agricultural_system.generate_streaming_response(
                message, session_id, coordinates, **kwargs
            ):
                yield chunk, is_complete
                
        except Exception as e:
            logger.error(f"ChatService error: {e}")
            yield (f"Service Error: {str(e)}", True)
    
    async def generate_complete_response(
        self, 
        message: str, 
        **kwargs
    ) -> str:
        """Generate complete response using agricultural advisor"""
        try:
            # Use agricultural advisor system for all queries
            session_id = kwargs.get('session_id', self._create_session_id())
            coordinates = kwargs.get('coordinates', None)
            
            logger.info(f"Processing query with agricultural system, session: {session_id}")
            
            # Use the agricultural system for complete response
            return await self.agricultural_system.generate_complete_response(
                message, session_id, coordinates, **kwargs
            )
                
        except Exception as e:
            logger.error(f"ChatService error: {e}")
            return f"Service Error: {str(e)}"
    
    def get_system_status(self) -> Dict[str, any]:
        """Get system status and capabilities"""
        return {
            "agricultural_system_available": True,
            "api_keys_configured": {
                "gemini": bool(Config.GEMINI_API_KEY),
                "weather": bool(Config.WEATHER_API_KEY),
                "exa": bool(Config.EXA_API_KEY)
            },
            "capabilities": [
                "agricultural_advice",
                "weather_integration", 
                "crop_management",
                "pest_identification",
                "irrigation_scheduling",
                "fertilizer_recommendations",
                "intelligent_query_understanding"
            ]
        }

# Global instance - can be imported directly
chat_service = ChatService()

# Convenience functions for easy import (maintains existing interface)
async def generate_streaming_response(message: str, **kwargs) -> AsyncGenerator[Tuple[str, bool], None]:
    """Convenience function for streaming response"""
    async for chunk, is_complete in chat_service.generate_streaming_response(message, **kwargs):
        yield chunk, is_complete

async def generate_complete_response(message: str, **kwargs) -> str:
    """Convenience function for complete response"""
    return await chat_service.generate_complete_response(message, **kwargs)

def get_system_status() -> Dict[str, any]:
    """Get system status and capabilities"""
    return chat_service.get_system_status()