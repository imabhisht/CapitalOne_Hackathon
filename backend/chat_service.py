# chat_service.py
import asyncio
from typing import AsyncGenerator, Tuple, Optional, Dict, Any
from abc import ABC, abstractmethod
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseChatProvider(ABC):
    """
    Abstract base class for different chat providers (OpenAI, Anthropic, local models, etc.)
    """
    
    @abstractmethod
    async def generate_streaming_response(self, message: str, **kwargs) -> AsyncGenerator[Tuple[str, bool], None]:
        """Generate streaming response"""
        pass
    
    @abstractmethod
    async def generate_complete_response(self, message: str, **kwargs) -> str:
        """Generate complete response"""
        pass

class StaticChatProvider(BaseChatProvider):
    """
    Static/Mock provider for testing and development
    """
    
    def __init__(self, delay: float = 0.1):
        self.delay = delay
    
    async def generate_streaming_response(self, message: str, **kwargs) -> AsyncGenerator[Tuple[str, bool], None]:
        """Generate static streaming response for testing"""
        response_text = f"Echo: '{message}'. This is a static response from StaticChatProvider. Replace this provider with your actual AI implementation."
        
        words = response_text.split()
        
        for word in words:
            yield (word + " ", False)
            await asyncio.sleep(self.delay)
        
        yield ("", True)  # Signal completion
    
    async def generate_complete_response(self, message: str, **kwargs) -> str:
        """Generate complete static response"""
        accumulated = ""
        async for chunk, is_complete in self.generate_streaming_response(message, **kwargs):
            if is_complete:
                break
            accumulated += chunk
        return accumulated.strip()

class OpenAIChatProvider(BaseChatProvider):
    """
    OpenAI provider - ready for integration
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        # Import OpenAI client when needed
        # from openai import AsyncOpenAI
        # self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate_streaming_response(self, message: str, **kwargs) -> AsyncGenerator[Tuple[str, bool], None]:
        """
        OpenAI streaming implementation
        Uncomment and implement when ready to use OpenAI
        """
        # Example implementation:
        """
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": message}],
                temperature=self.temperature,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content is not None:
                    yield (content, False)
            
            yield ("", True)  # Signal completion
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            yield (f"Error: {str(e)}", True)
        """
        
        # Placeholder implementation
        yield ("OpenAI provider not implemented yet. Please uncomment and configure the actual implementation.", True)
    
    async def generate_complete_response(self, message: str, **kwargs) -> str:
        accumulated = ""
        async for chunk, is_complete in self.generate_streaming_response(message, **kwargs):
            if is_complete:
                break
            accumulated += chunk
        return accumulated.strip()

class AnthropicChatProvider(BaseChatProvider):
    """
    Anthropic provider - ready for integration
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", max_tokens: int = 1000):
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        # Import Anthropic client when needed
        # import anthropic
        # self.client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def generate_streaming_response(self, message: str, **kwargs) -> AsyncGenerator[Tuple[str, bool], None]:
        """
        Anthropic streaming implementation
        Uncomment and implement when ready to use Anthropic
        """
        # Example implementation:
        """
        try:
            async with self.client.messages.stream(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": message}],
                **kwargs
            ) as stream:
                async for text in stream.text_stream:
                    yield (text, False)
            
            yield ("", True)  # Signal completion
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            yield (f"Error: {str(e)}", True)
        """
        
        # Placeholder implementation
        yield ("Anthropic provider not implemented yet. Please uncomment and configure the actual implementation.", True)
    
    async def generate_complete_response(self, message: str, **kwargs) -> str:
        accumulated = ""
        async for chunk, is_complete in self.generate_streaming_response(message, **kwargs):
            if is_complete:
                break
            accumulated += chunk
        return accumulated.strip()

class RAGChatProvider(BaseChatProvider):
    """
    Custom RAG provider - ready for your implementation
    """
    
    def __init__(self, vector_store=None, llm_provider=None, **config):
        self.vector_store = vector_store
        self.llm_provider = llm_provider
        self.config = config
    
    async def _retrieve_context(self, query: str) -> str:
        """Retrieve relevant context from vector store"""
        # Implement your RAG retrieval logic here
        # Example:
        """
        if self.vector_store:
            results = await self.vector_store.similarity_search(query, k=5)
            return "\n".join([doc.page_content for doc in results])
        """
        return f"[Context for: {query}] - Implement your RAG retrieval logic here"
    
    async def generate_streaming_response(self, message: str, **kwargs) -> AsyncGenerator[Tuple[str, bool], None]:
        """Generate RAG-enhanced streaming response"""
        try:
            # Step 1: Retrieve context
            context = await self._retrieve_context(message)
            
            # Step 2: Create enhanced prompt
            enhanced_prompt = f"""Context: {context}
            
User Question: {message}

Please provide a helpful response based on the context above."""
            
            # Step 3: Generate response using your preferred LLM
            # This is where you'd call your LLM provider with the enhanced prompt
            # For now, return a placeholder
            response = f"RAG Response for: '{message}'\nContext used: {context[:100]}...\nImplement your LLM call here."
            
            words = response.split()
            for word in words:
                yield (word + " ", False)
                await asyncio.sleep(0.05)
            
            yield ("", True)
            
        except Exception as e:
            logger.error(f"RAG provider error: {e}")
            yield (f"RAG Error: {str(e)}", True)
    
    async def generate_complete_response(self, message: str, **kwargs) -> str:
        accumulated = ""
        async for chunk, is_complete in self.generate_streaming_response(message, **kwargs):
            if is_complete:
                break
            accumulated += chunk
        return accumulated.strip()

class ChatService:
    """
    Main ChatService that manages different providers and handles routing
    """
    
    def __init__(self, default_provider: str = "static"):
        self.providers: Dict[str, BaseChatProvider] = {}
        self.default_provider = default_provider
        self._initialize_default_providers()
    
    def _initialize_default_providers(self):
        """Initialize default providers"""
        self.providers["static"] = StaticChatProvider()
        # Add other providers as needed
        # self.providers["openai"] = OpenAIChatProvider(api_key="your-key")
        # self.providers["anthropic"] = AnthropicChatProvider(api_key="your-key")
        # self.providers["rag"] = RAGChatProvider()
    
    def add_provider(self, name: str, provider: BaseChatProvider):
        """Add a custom provider"""
        self.providers[name] = provider
    
    def set_default_provider(self, provider_name: str):
        """Set the default provider"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not found")
        self.default_provider = provider_name
    
    async def generate_streaming_response(
        self, 
        message: str, 
        provider: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[Tuple[str, bool], None]:
        """
        Generate streaming response using specified provider
        
        Args:
            message: User's input message
            provider: Provider name (uses default if None)
            **kwargs: Additional arguments passed to provider
            
        Yields:
            Tuple[str, bool]: (content_chunk, is_complete)
        """
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            yield (f"Error: Provider '{provider_name}' not found", True)
            return
        
        try:
            chat_provider = self.providers[provider_name]
            async for chunk, is_complete in chat_provider.generate_streaming_response(message, **kwargs):
                yield (chunk, is_complete)
        except Exception as e:
            logger.error(f"ChatService error: {e}")
            yield (f"Service Error: {str(e)}", True)
    
    async def generate_complete_response(
        self, 
        message: str, 
        provider: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate complete response (non-streaming)"""
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            return f"Error: Provider '{provider_name}' not found"
        
        try:
            chat_provider = self.providers[provider_name]
            return await chat_provider.generate_complete_response(message, **kwargs)
        except Exception as e:
            logger.error(f"ChatService error: {e}")
            return f"Service Error: {str(e)}"
    
    def get_available_providers(self) -> list:
        """Get list of available providers"""
        return list(self.providers.keys())

# Global instance - can be imported directly
chat_service = ChatService()

# Convenience functions for easy import
async def generate_streaming_response(message: str, provider: Optional[str] = None, **kwargs):
    """Convenience function for streaming response"""
    async for chunk, is_complete in chat_service.generate_streaming_response(message, provider, **kwargs):
        yield chunk, is_complete

async def generate_complete_response(message: str, provider: Optional[str] = None, **kwargs) -> str:
    """Convenience function for complete response"""
    return await chat_service.generate_complete_response(message, provider, **kwargs)