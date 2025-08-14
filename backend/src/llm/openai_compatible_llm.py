from openai import OpenAI
import os
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage


# Generic LLM wrapper using OpenAI SDK specification
class OpenAICompatibleLLM:
    def __init__(self, model=None, api_key=None, base_url=None):
        """
        Initialize LLM client using OpenAI SDK format
        
        Args:
            model: LLM model name (e.g., "gpt-4", "gemini-2.5-flash", "claude-3-sonnet")
            api_key: LLM API key (if None, will use LLM_API_KEY env var)
            base_url: API base URL (if None, will use LLM_BASE_URL env var)
        """
        self.model = model or os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.client = OpenAI(
            api_key=api_key or os.getenv("LLM_API_KEY"),
            base_url=base_url or os.getenv("LLM_BASE_URL")
        )
    
    def invoke(self, messages, temperature=0.7, max_tokens=1000):
        """
        Invoke LLM with messages using OpenAI specification
        
        Args:
            messages: List of BaseMessage objects
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
        """
        # Convert LangChain messages to OpenAI format
        openai_messages = []
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                openai_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                openai_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                openai_messages.append({"role": "assistant", "content": msg.content})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            return AIMessage(content=content)
            
        except Exception as e:
            return AIMessage(content=f"Error calling LLM: {str(e)}")