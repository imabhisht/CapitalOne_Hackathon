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
from src.agents.langraph_agent import LangGraphAgent
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
        
        # Initialize LangGraph Agent
        self.agent = LangGraphAgent(self.llm)
        
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
            logger.info(f"_process_message called with message: {message}")
            logger.info(f"_process_message conversation_history length: {len(conversation_history) if conversation_history else 0}")
            
            # Use LangGraph Agent instead of direct LLM call
            async for chunk, is_complete in self.agent.stream_invoke(message, conversation_history):
                yield (chunk, is_complete)
            
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
            conversation_history = []  # Session-specific conversation history
            
            if request.session_id:
                # Try to load existing session
                try:
                    chat_session = ChatSession(
                        user_id=request.user_id,
                        session_id=request.session_id,
                        refresh=True
                    )
                    # Get conversation history for context
                    messages = await chat_session.get_messages(refresh=True, limit=10)
                    logger.info(f"Loaded existing session {request.session_id} with {len(messages)} messages")
                    
                    # Convert to LLM format
                    for msg in messages:
                        if msg.message_type == "human":
                            conversation_history.append(HumanMessage(content=msg.content))
                        elif msg.message_type == "ai":
                            conversation_history.append(AIMessage(content=msg.content))
                except Exception as e:
                    logger.warning(f"Could not load session {request.session_id}: {e}. Creating new session.")
                    # Create new session if loading fails
                    chat_session = ChatSession(
                        user_id=request.user_id,
                        title=f"Chat Session {request.message[:30]}..."
                    )
                    logger.info(f"Created new session for user {request.user_id}")
            else:
                # Create new session - this should only happen for the very first message
                chat_session = ChatSession(
                    user_id=request.user_id,
                    title=f"Chat Session {request.message[:30]}..."
                )
                logger.info(f"Created new session for user {request.user_id} (no session_id provided)")

            # Store human message immediately
            await chat_session.add_message(
                content=request.message,
                message_type="human",
                language_type=getattr(request, 'language_type', 'en'),
                metadata=getattr(request, 'metadata', {}),
                sync_to_db=True
            )

            # Store the session ID for potential retrieval
            self._current_session_id = chat_session.id if chat_session else None
            
            # Generate AI response with conversation context
            accumulated_response = ""
            logger.info(f"Conversation history length: {len(conversation_history)}")
            
            # send only the last 10 messages to the agent
            conversation_history = conversation_history[-10:]
            
            async for chunk, is_complete in self._process_message(request.message, conversation_history):
                if not is_complete:
                    accumulated_response += chunk

                # Store AI response when streaming is complete
                if is_complete:
                    logger.info(f"Streaming complete. Accumulated response length: {len(accumulated_response)}")
                    if accumulated_response.strip():
                        logger.info(f"Saving AI response: '{accumulated_response[:50]}...'")
                        await chat_session.add_message(
                            content=accumulated_response.strip(),
                            message_type="ai",
                            language_type=getattr(request, 'language_type', 'en'),
                            metadata={"generated_by": "gemini_llm", "model": "gemini-2.0-flash-exp"},
                            sync_to_db=True
                        )
                        logger.info(f"AI message saved for session: {chat_session.id}")
                    else:
                        logger.warning(f"No accumulated response to save")

                yield (chunk, is_complete)

        except Exception as e:
            logger.error(f"Error during streaming response: {e}")
            yield (f"Error: {str(e)}", True)

    def get_current_session_id(self) -> str:
        """Get the current session ID from the last processed request"""
        return getattr(self, '_current_session_id', None)


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