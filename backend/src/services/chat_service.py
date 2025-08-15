# src/services/chat_service.py

import asyncio
from typing import AsyncGenerator, Tuple
import logging
import os

# Models
from src.models.chat_request import ChatRequest, ChatResponse
from src.models.chat_session import ChatSession

# LLM and Agent imports
from src.llm.openai_compatible_llm import OpenAICompatibleLLM
from src.agents.langraph_agent import LangGraphAgent
from src.services.multi_agent_service import multi_agent_service
from src.services.routing_service import routing_service
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatService:
    """
    Enhanced ChatService with OpenAI-compatible LLM integration.
    Supports both simple LLM responses and multi-agent workflows.
    """

    def __init__(self):
        # Initialize OpenAI-compatible LLM (main model)
        self.llm = OpenAICompatibleLLM(
            model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
        )
        
        # Initialize small LLM for routing and simple tasks
        self.small_llm = OpenAICompatibleLLM(
            model=os.getenv("SMALL_LLM_MODEL", "gpt-3.5-turbo"),
            api_key=os.getenv("SMALL_LLM_API_KEY"),
            base_url=os.getenv("SMALL_LLM_BASE_URL")
        )
        
        # Initialize LangGraph Agent with main LLM
        self.agent = LangGraphAgent(self.llm)
        
        # Initialize small agent for simple tasks
        self.small_agent = LangGraphAgent(self.small_llm)
        
        # Multi-agent mode flag (can be set via environment variable)
        self.use_multi_agent = os.getenv("USE_MULTI_AGENT", "true").lower() == "true"
        
        # Enable smart routing (can be disabled via environment variable)
        self.use_smart_routing = os.getenv("USE_SMART_ROUTING", "true").lower() == "true"
        
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
        Core logic to process the message using smart routing, multi-agent system, or single LangGraph agent.
        """
        try:
            logger.info(f"_process_message called with message: {message}")
            logger.info(f"_process_message conversation_history length: {len(conversation_history) if conversation_history else 0}")
            logger.info(f"Using multi-agent mode: {self.use_multi_agent}")
            
            # Choose processing method based on configuration for complex tasks
            if self.use_multi_agent and multi_agent_service.is_available():
                logger.info(f"Using multi-agent system for message: '{message}'")
                # Create a ChatRequest for the multi-agent service
                from src.models.chat_request import ChatRequest
                
                # Convert conversation history to the format expected by multi-agent service
                history_for_multi_agent = []
                if conversation_history:
                    for msg in conversation_history:
                        if isinstance(msg, HumanMessage):
                            history_for_multi_agent.append({"role": "user", "content": msg.content})
                        elif isinstance(msg, AIMessage):
                            history_for_multi_agent.append({"role": "assistant", "content": msg.content})
                
                request = ChatRequest(
                    message=message,
                    conversation_history=history_for_multi_agent
                )
                
                # Use multi-agent system
                async for chunk, is_complete in multi_agent_service.generate_streaming_response(request):
                    yield (chunk, is_complete)
            else:
                logger.info(f"Using single LangGraph agent for message: '{message}' (multi_agent: {self.use_multi_agent}, available: {multi_agent_service.is_available()})")
                # Use single LangGraph Agent (main LLM)
                async for chunk, is_complete in self.agent.stream_invoke(message, conversation_history):
                    yield (chunk, is_complete)
            
        except Exception as e:
            logger.error(f"Error in message processing: {e}")
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
        Generate streaming response using OpenAI-compatible LLM.
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
                            metadata={"generated_by": "openai_compatible_llm", "model": os.getenv("LLM_MODEL", "gpt-3.5-turbo")},
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