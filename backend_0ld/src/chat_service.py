import asyncio
from typing import AsyncGenerator, Tuple, Optional, Dict
import logging
from datetime import datetime
import uuid

from .agent import agricultural_system
from .config import Config

logger = logging.getLogger(__name__)

class AgriculturalChatService:
    """Agricultural AI Advisor Chat Service"""
    
    def __init__(self):
        self.system = agricultural_system
    
    async def generate_streaming_response(
        self, 
        message: str, 
        session_id: str = None,
        coordinates: Dict[str, float] = None,
        **kwargs
    ) -> AsyncGenerator[Tuple[str, bool], None]:
        """
        Generate streaming response for agricultural advice
        
        Args:
            message: User's input message
            session_id: Chat session ID (auto-generated if not provided)
            coordinates: Optional lat/lon coordinates for weather data
            **kwargs: Additional arguments
            
        Yields:
            Tuple[str, bool]: (content_chunk, is_complete)
        """
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Use the agricultural system for streaming response
            async for chunk, is_complete in self.system.generate_streaming_response(
                message, session_id, coordinates, **kwargs
            ):
                yield chunk, is_complete
                
        except Exception as e:
            logger.error(f"Agricultural chat service streaming error: {e}")
            yield (f"Service Error: {str(e)}", True)
    
    async def generate_complete_response(
        self, 
        message: str, 
        session_id: str = None,
        coordinates: Dict[str, float] = None,
        **kwargs
    ) -> str:
        """Generate complete response for agricultural advice"""
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Use the agricultural system for complete response
            return await self.system.generate_complete_response(
                message, session_id, coordinates, **kwargs
            )
            
        except Exception as e:
            logger.error(f"Agricultural chat service error: {e}")
            return f"Service Error: {str(e)}"
    
    def get_session_id(self) -> str:
        """Generate a new session ID"""
        return str(uuid.uuid4())

# Global instance
agricultural_chat_service = AgriculturalChatService()

# Convenience functions for easy import (matching the original chat_service.py interface)
async def generate_streaming_response(
    message: str, 
    session_id: str = None,
    coordinates: Dict[str, float] = None,
    **kwargs
) -> AsyncGenerator[Tuple[str, bool], None]:
    """Convenience function for streaming response"""
    async for chunk, is_complete in agricultural_chat_service.generate_streaming_response(
        message, session_id, coordinates, **kwargs
    ):
        yield chunk, is_complete

async def generate_complete_response(
    message: str, 
    session_id: str = None,
    coordinates: Dict[str, float] = None,
    **kwargs
) -> str:
    """Convenience function for complete response"""
    return await agricultural_chat_service.generate_complete_response(
        message, session_id, coordinates, **kwargs
    )

def create_session() -> str:
    """Create a new chat session"""
    return agricultural_chat_service.get_session_id() 