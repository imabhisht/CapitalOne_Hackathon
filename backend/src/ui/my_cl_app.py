# src/services/chat_service.py

import asyncio
from typing import AsyncGenerator, Tuple
import logging

# Models
from src.models.chat_request import ChatRequest, ChatResponse
from src.models.chat_session import ChatSession

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
        request: ChatRequest, 
        **kwargs
    ) -> AsyncGenerator[Tuple[str, bool], None]:
        """
        Generate streaming response using the built-in logic.
        Also handles storing messages to MongoDB.
        
        Yields:
            Tuple[str, bool]: (content_chunk, is_complete)
        """
        if not request.message.strip():
            yield ("Error: Empty message received.", True)
            return

        try:
            # Get or create chat session
            chat_session = None
            if hasattr(request, 'session_id') and request.session_id:
                # Try to load existing session
                chat_session = ChatSession(
                    user_id=request.user_id,
                    session_id=request.session_id,
                    refresh=True
                )
            else:
                # Create new session
                chat_session = ChatSession(
                    user_id=request.user_id,
                    title=f"Chat Session {request.message[:30]}..."  # Use first 30 chars of message as title
                )

            # Store human message immediately
            await chat_session.add_message(
                content=request.message,
                message_type="human",
                language_type=getattr(request, 'language_type', 'en'),
                metadata=getattr(request, 'metadata', {}),
                sync_to_db=True
            )

            # Generate AI response
            accumulated_response = ""
            async for chunk, is_complete in self._process_message(request.message):
                if not is_complete:
                    accumulated_response += chunk
                yield (chunk, is_complete)

            # Store AI response once streaming is complete
            if accumulated_response.strip():
                await chat_session.add_message(
                    content=accumulated_response.strip(),
                    message_type="ai",
                    language_type=getattr(request, 'language_type', 'en'),
                    metadata={"generated_by": "static_response"},
                    sync_to_db=True
                )

            logger.info(f"Messages stored for session: {chat_session.id}")

        except Exception as e:
            logger.error(f"Error during streaming response: {e}")
            yield (f"Error: {str(e)}", True)


# Global instance
chat_service = ChatService()

# Convenience functions
async def generate_streaming_response(request: ChatRequest, **kwargs):
    """Convenience function to stream response."""
    async for chunk, is_complete in chat_service.generate_streaming_response(request=request, **kwargs):
        yield chunk, is_complete