import asyncio
from typing import AsyncGenerator, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatService:
    """Simple ChatService for generating static responses"""
    
    def __init__(self, delay: float = 0.1):
        self.delay = delay
    
    async def generate_streaming_response(
        self, 
        message: str, 
        **kwargs
    ) -> AsyncGenerator[Tuple[str, bool], None]:
        """
        Generate streaming response for testing
        
        Args:
            message: User's input message
            **kwargs: Additional arguments (ignored in this implementation)
            
        Yields:
            Tuple[str, bool]: (content_chunk, is_complete)
        """
        try:
            response_text = f"Echo: '{message}'. This is a static response from ChatService."
            words = response_text.split()
            
            for word in words:
                yield (word + " ", False)
                await asyncio.sleep(self.delay)
            
            yield ("", True)  # Signal completion
        except Exception as e:
            logger.error(f"ChatService error: {e}")
            yield (f"Service Error: {str(e)}", True)
    
    async def generate_complete_response(
        self, 
        message: str, 
        **kwargs
    ) -> str:
        """Generate complete static response"""
        try:
            accumulated = ""
            async for chunk, is_complete in self.generate_streaming_response(message, **kwargs):
                if is_complete:
                    break
                accumulated += chunk
            return accumulated.strip()
        except Exception as e:
            logger.error(f"ChatService error: {e}")
            return f"Service Error: {str(e)}"

# Global instance - can be imported directly
chat_service = ChatService()

# Convenience functions for easy import
async def generate_streaming_response(message: str, **kwargs) -> AsyncGenerator[Tuple[str, bool], None]:
    """Convenience function for streaming response"""
    async for chunk, is_complete in chat_service.generate_streaming_response(message, **kwargs):
        yield chunk, is_complete

async def generate_complete_response(message: str, **kwargs) -> str:
    """Convenience function for complete response"""
    return await chat_service.generate_complete_response(message, **kwargs)