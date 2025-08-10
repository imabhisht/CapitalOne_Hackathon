# chat_service.py
import asyncio
from typing import AsyncGenerator, Tuple
import logging

# Models
from src.models.chat_request import ChatRequest, ChatResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatService:
    """
    Simplified ChatService with a single built-in response logic.
    No provider switching — only one default behavior.
    """

    def __init__(self):
        # You can initialize your LLM client, vector store, etc. here
        # For example: self.llm = AsyncOpenAI(api_key="...")
        pass

    async def _process_message(self, message: str) -> AsyncGenerator[Tuple[str, bool], None]:
        """
        Core logic to process the message and yield response chunks.
        Replace this method with actual LLM call, RAG, etc.
        """
        # Simulate streaming response
        response_text = f"Echo: '{message}'. This is a static streaming response. Replace this logic with your actual AI backend."

        words = response_text.split()
        for word in words:
            yield (word + " ", False)
            await asyncio.sleep(0.05)  # Simulate network delay or token generation

        yield ("", True)  # Signal completion

    async def generate_streaming_response(
        self, 
        message: ChatRequest, 
        **kwargs
    ) -> AsyncGenerator[Tuple[str, bool], None]:
        """
        Generate streaming response using the built-in logic.
        
        Yields:
            Tuple[str, bool]: (content_chunk, is_complete)
        """
        if not message.strip():
            yield ("Error: Empty message received.", True)
            return

        try:
            async for chunk, is_complete in self._process_message(message):
                yield (chunk, is_complete)
        except Exception as e:
            logger.error(f"Error during streaming response: {e}")
            yield (f"Error: {str(e)}", True)

    # async def generate_complete_response(
    #     self, 
    #     message: str, 
    #     **kwargs
    # ) -> str:
    #     """
    #     Generate complete response by accumulating streaming output.
    #     """
    #     if not message.strip():
    #         return "Error: Empty message received."

    #     try:
    #         accumulated = ""
    #         async for chunk, is_complete in self.generate_streaming_response(message, **kwargs):
    #             if is_complete:
    #                 break
    #             accumulated += chunk
    #         return accumulated.strip()
    #     except Exception as e:
    #         logger.error(f"Error during complete response: {e}")
    #         return f"Service Error: {str(e)}"


# Global instance
chat_service = ChatService()

# Convenience functions
async def generate_streaming_response(request: ChatRequest, **kwargs):
    """Convenience function to stream response."""
    async for chunk, is_complete in chat_service.generate_streaming_response(request=request, **kwargs):
        yield chunk, is_complete

# async def generate_complete_response(request: ChatRequest, **kwargs) -> str:
#     """Convenience function to get full response."""
#     return await chat_service.generate_complete_response(request=request, **kwargs)