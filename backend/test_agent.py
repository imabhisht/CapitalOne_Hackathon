"""
Test script for the LangGraph agent.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.llm.gemini_llm import GeminiLLM
from src.agents.langraph_agent import LangGraphAgent

async def test_agent():
    """Test the LangGraph agent with various queries."""
    
    # Initialize LLM and Agent
    llm = GeminiLLM(
        model="gemini-2.0-flash-exp",
        api_key=os.getenv("GEMINI_API_KEY")
    )
    
    agent = LangGraphAgent(llm)
    
    # Test queries
    test_queries = [
        "What's the location information for Baroda?",
        "Can you get the weather for Baroda, Jamjodhpur?",
        "Calculate 25 * 4 + 10",
        "Hello, how are you?",
        "What can you help me with?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        
        try:
            # Test streaming response
            response_parts = []
            async for chunk, is_complete in agent.stream_invoke(query):
                if not is_complete:
                    response_parts.append(chunk)
                    print(chunk, end='', flush=True)
                else:
                    print("\n")
                    break
            
            full_response = ''.join(response_parts).strip()
            print(f"\nFull Response: {full_response}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "-"*50)

if __name__ == "__main__":
    asyncio.run(test_agent())