# src/services/chat_service.py

import asyncio
from typing import AsyncGenerator, Tuple
import logging
import os

# Models
from src.models.chat_request import ChatRequest, ChatResponse
from src.models.chat_session import ChatSession

# LLM and Agent imports
from src.llm.gemini_llm import GeminiLLM
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatService:
    """
    Enhanced ChatService with Gemini LLM integration.
    Supports both simple LLM responses and multi-agent workflows.
    """

    def __init__(self):
        # Initialize Gemini LLM
        self.llm = GeminiLLM(
            model="gemini-2.0-flash-exp",  # Using the latest model
            api_key=os.getenv("GEMINI_API_KEY")
        )
        
        # System prompt for the assistant
        self.system_prompt = """You are a helpful AI assistant for CapitalOne. You can help users with:

1. General questions and conversations
2. Financial advice and information
3. Data analysis and insights
4. Weather information
5. Calculations and problem-solving

Please be helpful, accurate, and conversational. If you need more information to help the user, ask clarifying questions.
"""

    async def _process_message(self, message: str, conversation_history: list = None) -> AsyncGenerator[Tuple[str, bool], None]:
        """
        Core logic to process the message using Gemini LLM and yield response chunks.
        """
        try:
            # Prepare messages for the LLM
            messages = [SystemMessage(content=self.system_prompt)]
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Keep last 10 messages for context
            
            # Add current user message
            messages.append(HumanMessage(content=message))
            
            # Get response from Gemini
            logger.info(f"Sending message to Gemini: {message}")
            response = self.llm.invoke(messages, temperature=0.7, max_tokens=2000)
            
            # Stream the response word by word to simulate streaming
            response_text = response.content
            words = response_text.split()
            
            for i, word in enumerate(words):
                yield (word + " ", False)
                await asyncio.sleep(0.03)  # Simulate streaming delay
            
            yield ("", True)  # Signal completion
            
        except Exception as e:
            logger.error(f"Error in LLM processing: {e}")
            error_message = f"I apologize, but I encountered an error: {str(e)}"
            words = error_message.split()
            for word in words:
                yield (word + " ", False)
                await asyncio.sleep(0.03)
            yield ("", True)

    async def generate_streaming_response(
        self, 
        request: ChatRequest, 
        **kwargs
    ) -> AsyncGenerator[Tuple[str, bool], None]:
        """
        Generate streaming response using Gemini LLM.
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
            conversation_history = []
            
            if hasattr(request, 'session_id') and request.session_id:
                # Try to load existing session
                chat_session = ChatSession(
                    user_id=request.user_id,
                    session_id=request.session_id,
                    refresh=True
                )
                # Get conversation history for context
                messages = await chat_session.get_messages(refresh=True, limit=10)
                # Convert to LLM format
                for msg in messages:
                    if msg.message_type == "human":
                        conversation_history.append(HumanMessage(content=msg.content))
                    elif msg.message_type == "ai":
                        conversation_history.append(AIMessage(content=msg.content))
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

            # Generate AI response with conversation context
            accumulated_response = ""
            async for chunk, is_complete in self._process_message(request.message, conversation_history):
                if not is_complete:
                    accumulated_response += chunk
                yield (chunk, is_complete)

            # Store AI response once streaming is complete
            if accumulated_response.strip():
                await chat_session.add_message(
                    content=accumulated_response.strip(),
                    message_type="ai",
                    language_type=getattr(request, 'language_type', 'en'),
                    metadata={"generated_by": "gemini_llm", "model": "gemini-2.0-flash-exp"},
                    sync_to_db=True
                )

            logger.info(f"Messages stored for session: {chat_session.id}")

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