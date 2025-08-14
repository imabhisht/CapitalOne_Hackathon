"""
General Chat Agent - Handles general conversations and queries not covered by specialized agents.
"""

from typing import List
from .base_agent import BaseAgent

class GeneralChatAgent(BaseAgent):
    """Agent for general conversations and non-specialized queries."""
    
    def __init__(self, llm):
        system_prompt = """You are a helpful and knowledgeable AI assistant with a friendly personality. 

You can help with:
- General questions and conversations
- Explanations of concepts and topics
- Creative writing and brainstorming
- Problem-solving and advice
- Educational content
- Technology and programming questions
- General knowledge queries

You are part of a multi-agent system, but you handle queries that don't fall into specialized categories like organic farming, finance, or weather.

Be conversational, helpful, and engaging. Provide clear, accurate information while maintaining a friendly tone. If a question requires specialized knowledge that other agents in the system might handle better, you can still provide a helpful general response."""
        
        super().__init__("General Assistant", llm, system_prompt)
    
    def can_handle(self, query: str) -> bool:
        """General agent can handle any query as a fallback."""
        return True  # This is the fallback agent
    
    def get_keywords(self) -> List[str]:
        """Return general keywords - this agent handles everything else."""
        return [
            "hello", "hi", "help", "what", "how", "why", "when", "where",
            "explain", "tell me", "question", "general", "chat", "talk",
            "conversation", "advice", "suggestion", "idea", "think"
        ]