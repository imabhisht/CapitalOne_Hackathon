import openai
from typing import AsyncGenerator, Tuple, Optional
import logging
from .config import Config

logger = logging.getLogger(__name__)

class GeminiClient:
    """Gemini LLM client using OpenAI SDK"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=Config.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/models"
        )
        self.model = Config.GEMINI_MODEL
    
    async def generate_streaming_response(
        self, 
        messages: list, 
        **kwargs
    ) -> AsyncGenerator[Tuple[str, bool], None]:
        """
        Generate streaming response from Gemini
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional parameters
            
        Yields:
            Tuple[str, bool]: (content_chunk, is_complete)
        """
        try:
            if not Config.GEMINI_API_KEY:
                # Fallback response if no API key
                fallback = "I'm sorry, but I need a valid Gemini API key to provide agricultural advice. Please configure your API key."
                yield (fallback, True)
                return
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                max_tokens=kwargs.get("max_tokens", Config.MAX_TOKENS),
                temperature=kwargs.get("temperature", Config.TEMPERATURE)
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield (content, False)
            
            yield ("", True)  # Signal completion
            
        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            yield (f"Error generating response: {str(e)}", True)
    
    async def generate_complete_response(
        self, 
        messages: list, 
        **kwargs
    ) -> str:
        """Generate complete response from Gemini"""
        try:
            if not Config.GEMINI_API_KEY:
                return "I'm sorry, but I need a valid Gemini API key to provide agricultural advice. Please configure your API key."
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
                max_tokens=kwargs.get("max_tokens", Config.MAX_TOKENS),
                temperature=kwargs.get("temperature", Config.TEMPERATURE)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Gemini complete response error: {e}")
            return f"Error generating response: {str(e)}"

# Global instance
gemini_client = GeminiClient() 