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
        from src.llm.gemini_llm import GeminiLLM
        
        print("✅ Imports successful")
        
        # Initialize LLM and Agent
        llm = GeminiLLM(
            model="gemini-2.0-flash-exp",
            api_key=os.getenv("GEMINI_API_KEY")
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