#!/usr/bin/env python3
"""
Minimal test to isolate the issue.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.llm.openai_compatible_llm import OpenAICompatibleLLM
from src.agents.iterative_agent import IterativeAgent

# Load environment variables
load_dotenv()

async def test_minimal():
    """Minimal test of iterative agent."""
    
    print("🔬 Minimal Iterative Agent Test")
    print("=" * 40)
    
    # Initialize LLM
    try:
        llm = OpenAICompatibleLLM(
            model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
        )
        print("✅ LLM initialized")
    except Exception as e:
        print(f"❌ LLM initialization failed: {e}")
        return
    
    # Initialize iterative agent
    try:
        agent = IterativeAgent(llm, max_iterations=3)
        print("✅ Iterative agent initialized")
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return
    
    # Test query
    query = "what is the weather?"
    print(f"\n🔍 Testing: '{query}'")
    print("-" * 30)
    
    try:
        print("📡 Streaming response:")
        async for chunk, is_complete, step_info in agent.stream_process_iteratively(query):
            if not is_complete:
                print(chunk, end="", flush=True)
            else:
                print(f"\n\n✅ Complete! Step info: {step_info}")
                break
                
    except Exception as e:
        print(f"❌ Error during streaming: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Starting Minimal Test")
    
    # Check environment variables
    if not os.getenv("LLM_API_KEY"):
        print("❌ LLM_API_KEY not set")
        sys.exit(1)
    
    # Run test
    asyncio.run(test_minimal())