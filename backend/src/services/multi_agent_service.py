"""
Multi-Agent Service - Manages the multi-agent system with specialized agents.
"""

import logging
import os
from typing import List, AsyncGenerator, Tuple
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

from src.llm.openai_compatible_llm import OpenAICompatibleLLM
from src.agents.agent_coordinator import AgentCoordinator
from src.models.chat_request import ChatRequest

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class MultiAgentService:
    """Service for managing multi-agent conversations."""
    
    def __init__(self):
        print("INIT")
        self.coordinator = None
        self._initialize_coordinator()
    
    def _initialize_coordinator(self):
        """Initialize the agent coordinator with LLM."""
        print("Initializing Multi-Agent Coordinator")
        try:
            # Get API key from environment
            api_key = os.getenv("LLM_API_KEY")
            if not api_key:
                logger.warning("LLM_API_KEY not found in environment variables")
                return
            
            # Initialize LLM
            llm = OpenAICompatibleLLM(
                model=os.getenv("LLM_MODEL"),
                api_key=api_key,
                base_url=os.getenv("LLM_BASE_URL")
            )

            # Initialize Small LLM
            small_llm = OpenAICompatibleLLM(
                model=os.getenv("SMALL_LLM_MODEL", "gemma3:270m"),
                api_key=os.getenv("SMALL_LLM_API_KEY"),
                base_url=os.getenv("SMALL_LLM_BASE_URL")
            )

            # Initialize coordinator (only pass the main LLM for now)
            self.coordinator = AgentCoordinator(llm=llm, small_llm=small_llm)
            logger.info("Multi-agent coordinator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize multi-agent coordinator: {e}")
    
    def is_available(self) -> bool:
        """Check if the multi-agent service is available."""
        return self.coordinator is not None
    
    async def generate_streaming_response(self, request: ChatRequest) -> AsyncGenerator[Tuple[str, bool], None]:
        """
        Generate streaming response using the multi-agent system.
        
        Args:
            request: Chat request containing message and conversation history
            
        Yields:
            Tuple[str, bool]: (content_chunk, is_complete)
        """
        if not self.is_available():
            error_msg = "Multi-agent system is not available. Please check your configuration."
            logger.error(error_msg)
            yield (error_msg, True)
            return
        
        try:
            # Convert conversation history to BaseMessage objects
            conversation_history = []
            if hasattr(request, 'conversation_history') and request.conversation_history:
                for msg in request.conversation_history:
                    if msg.get('role') == 'user':
                        conversation_history.append(HumanMessage(content=msg.get('content', '')))
                    elif msg.get('role') == 'assistant':
                        conversation_history.append(AIMessage(content=msg.get('content', '')))
            
            # Stream response from coordinator
            async for chunk, is_complete in self.coordinator.stream_process_query(
                request.message, 
                conversation_history
            ):
                yield (chunk, is_complete)
                
        except Exception as e:
            logger.error(f"Error in multi-agent streaming response: {e}")
            error_msg = f"I apologize, but I encountered an error: {str(e)}"
            words = error_msg.split()
            for word in words:
                yield (word + " ", False)
            yield ("", True)
    
    async def get_response(self, request: ChatRequest) -> str:
        """
        Get a complete response from the multi-agent system.
        
        Args:
            request: Chat request containing message and conversation history
            
        Returns:
            Complete response string
        """
        if not self.is_available():
            return "Multi-agent system is not available. Please check your configuration."
        
        try:
            # Convert conversation history to BaseMessage objects
            conversation_history = []
            if hasattr(request, 'conversation_history') and request.conversation_history:
                for msg in request.conversation_history:
                    if msg.get('role') == 'user':
                        conversation_history.append(HumanMessage(content=msg.get('content', '')))
                    elif msg.get('role') == 'assistant':
                        conversation_history.append(AIMessage(content=msg.get('content', '')))
            
            # Get response from coordinator
            response = await self.coordinator.process_query(request.message, conversation_history)
            return response
            
        except Exception as e:
            logger.error(f"Error in multi-agent response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def get_agent_info(self) -> dict:
        """Get information about available agents."""
        if not self.is_available():
            return {"error": "Multi-agent system not available"}
        
        return self.coordinator.get_agent_info()

# Global instance
multi_agent_service = MultiAgentService()