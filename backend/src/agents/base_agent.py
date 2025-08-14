"""
Base agent class for all specialized agents.
"""

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator, Tuple
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from src.llm.openai_compatible_llm import OpenAICompatibleLLM

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all specialized agents."""
    
    def __init__(self, name: str, llm: OpenAICompatibleLLM, system_prompt: str):
        self.name = name
        self.llm = llm
        self.system_prompt = system_prompt
        
    @abstractmethod
    def can_handle(self, query: str) -> bool:
        """Determine if this agent can handle the given query."""
        pass
    
    @abstractmethod
    def get_keywords(self) -> List[str]:
        """Return keywords that this agent specializes in."""
        pass
    
    async def process(self, message: str, conversation_history: List[BaseMessage] = None) -> str:
        """Process a message and return a response."""
        try:
            messages = []
            
            # Add system message
            messages.append(SystemMessage(content=self.system_prompt))
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history[-5:])  # Keep last 5 messages
            
            # Add current user message
            messages.append(HumanMessage(content=message))
            
            # Get response from LLM
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error in {self.name} agent: {e}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    async def stream_process(self, message: str, conversation_history: List[BaseMessage] = None) -> AsyncGenerator[Tuple[str, bool], None]:
        """Stream the agent response."""
        try:
            response = await self.process(message, conversation_history)
            
            # Stream word by word
            words = response.split()
            for word in words:
                yield (word + " ", False)
                await asyncio.sleep(0.03)
            
            yield ("", True)  # Signal completion
            
        except Exception as e:
            logger.error(f"Error in {self.name} stream_process: {e}")
            error_message = f"I apologize, but I encountered an error: {str(e)}"
            words = error_message.split()
            for word in words:
                yield (word + " ", False)
                await asyncio.sleep(0.03)
            yield ("", True)