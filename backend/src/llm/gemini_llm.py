from openai import OpenAI
import os
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage


# Gemini LLM wrapper using OpenAI SDK
class GeminiLLM:
    def __init__(self, model="gemini-2.5-flash", api_key=None):
        """
        Initialize Gemini client using OpenAI SDK format
        
        Args:
            model: Gemini model name (e.g., "gemini-2.5-flash", "gemini-1.5-pro")
            api_key: Gemini API key (if None, will use GEMINI_API_KEY env var)
        """
        self.model = model
        self.client = OpenAI(
            api_key=api_key or os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    
    def invoke(self, messages, temperature=0.7, max_tokens=1000):
        """
        Invoke Gemini with messages
        
        Args:
            messages: List of BaseMessage objects
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
        """
        # Convert LangChain messages to OpenAI format for Gemini
        gemini_messages = []
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                gemini_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                gemini_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                gemini_messages.append({"role": "assistant", "content": msg.content})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=gemini_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            return AIMessage(content=content)
            
        except Exception as e:
            return AIMessage(content=f"Error calling Gemini: {str(e)}")