"""
Simple test for LangGraph agent functionality.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_langraph_basic():
    """Test basic LangGraph functionality without external dependencies."""
    
    try:
        from src.agents.langraph_agent import LangGraphAgent
        from src.llm.openai_compatible_llm import OpenAICompatibleLLM
        
        print("✅ Imports successful")
        
        # Initialize LLM and Agent
        llm = OpenAICompatibleLLM(
            model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
        )
        
        agent = LangGraphAgent(llm)
        print("✅ Agent initialized successfully")
        
        # Test simple query
        response = await agent.invoke("Hello, how are you?")
        print(f"✅ Simple query response: {response[:100]}...")
        
        # Test tool query
        response = await agent.invoke("What's the location information for Baroda?")
        print(f"✅ Tool query response: {response[:100]}...")
        
        print("\n🎉 LangGraph agent is working properly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_langraph_basic())