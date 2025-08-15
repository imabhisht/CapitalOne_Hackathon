# src/services/routing_service.py

import os
import logging
from typing import Tuple, Dict, Any
from src.llm.openai_compatible_llm import OpenAICompatibleLLM

logger = logging.getLogger(__name__)

class RoutingService:
    """
    Service to route requests to appropriate LLM based on complexity.
    Uses a small, fast model for routing decisions and simple tasks.
    """
    
    def __init__(self):
        # Initialize small LLM for routing and simple tasks
        self.small_llm = OpenAICompatibleLLM(
            model=os.getenv("SMALL_LLM_MODEL", "z-ai/glm-4.5-air:free"),
            api_key=os.getenv("SMALL_LLM_API_KEY"),
            base_url=os.getenv("SMALL_LLM_BASE_URL")
        )
        
        # Initialize main LLM for complex tasks
        self.main_llm = OpenAICompatibleLLM(
            model=os.getenv("LLM_MODEL", "z-ai/glm-4.5-air:free"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
        )
        
        # Define simple task patterns
        self.simple_patterns = [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "how are you", "what's your name", "who are you",
            "thank you", "thanks", "bye", "goodbye",
            "what time", "what date", "today",
            "yes", "no", "ok", "okay"
        ]
        
        # Define complex task keywords
        self.complex_keywords = [
            "analyze", "calculate", "explain", "compare", "research",
            "write", "create", "generate", "code", "programming",
            "financial", "investment", "loan", "mortgage", "credit",
            "data analysis", "machine learning", "ai", "algorithm"
        ]
    
    def classify_request_complexity(self, message: str) -> Tuple[str, float]:
        """
        Classify if a request is simple or complex.
        
        Args:
            message: User message to classify
            
        Returns:
            Tuple of (classification, confidence_score)
            classification: "simple" or "complex"
            confidence_score: 0.0 to 1.0
        """
        message_lower = message.lower().strip()
        
        # Check for simple patterns
        for pattern in self.simple_patterns:
            if pattern in message_lower:
                return "simple", 0.9
        
        # Check for complex keywords
        for keyword in self.complex_keywords:
            if keyword in message_lower:
                return "complex", 0.8
        
        # Use message length and structure as indicators
        word_count = len(message.split())
        
        if word_count <= 5:
            return "simple", 0.7
        elif word_count > 20:
            return "complex", 0.7
        
        # Check for question complexity
        if any(word in message_lower for word in ["how", "why", "what", "when", "where"]):
            if word_count > 10:
                return "complex", 0.6
            else:
                return "simple", 0.6
        
        # Default to simple for short messages, complex for longer ones
        if word_count <= 10:
            return "simple", 0.5
        else:
            return "complex", 0.5
    
    def should_use_small_llm(self, message: str) -> bool:
        """
        Determine if we should use the small LLM for this request.
        
        Args:
            message: User message
            
        Returns:
            bool: True if small LLM should be used
        """
        classification, confidence = self.classify_request_complexity(message)
        
        # Use small LLM for simple tasks with high confidence
        if classification == "simple" and confidence >= 0.7:
            return True
        
        # Use small LLM for very short messages
        if len(message.split()) <= 3:
            return True
        
        return False
    
    def get_appropriate_llm(self, message: str) -> Tuple[OpenAICompatibleLLM, str]:
        """
        Get the appropriate LLM for the given message.
        
        Args:
            message: User message
            
        Returns:
            Tuple of (llm_instance, model_type)
        """
        if self.should_use_small_llm(message):
            logger.info(f"Using small LLM for message: {message[:50]}...")
            return self.small_llm, "small"
        else:
            logger.info(f"Using main LLM for message: {message[:50]}...")
            return self.main_llm, "main"
    
    def get_routing_info(self, message: str) -> Dict[str, Any]:
        """
        Get detailed routing information for debugging.
        
        Args:
            message: User message
            
        Returns:
            Dict with routing details
        """
        classification, confidence = self.classify_request_complexity(message)
        use_small = self.should_use_small_llm(message)
        
        return {
            "message_length": len(message),
            "word_count": len(message.split()),
            "classification": classification,
            "confidence": confidence,
            "use_small_llm": use_small,
            "selected_model": "small" if use_small else "main"
        }

# Global instance
routing_service = RoutingService()