#!/usr/bin/env python3
"""
Debug script to test routing decisions.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.llm.openai_compatible_llm import OpenAICompatibleLLM
from src.agents.agent_coordinator import AgentCoordinator

# Load environment variables
load_dotenv()

async def test_routing():
    """Test routing decisions for various queries."""
    
    print("🔍 Testing Routing Decisions")
    print("=" * 50)
    
    # Initialize LLMs
    try:
        llm = OpenAICompatibleLLM(
            model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
        )
        
        small_llm = OpenAICompatibleLLM(
            model=os.getenv("SMALL_LLM_MODEL", "gpt-3.5-turbo"),
            api_key=os.getenv("SMALL_LLM_API_KEY"),
            base_url=os.getenv("SMALL_LLM_BASE_URL")
        )
        
        print("✅ LLMs initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize LLMs: {e}")
        return
    
    # Initialize coordinator
    coordinator = AgentCoordinator(llm, small_llm)
    print("✅ Agent coordinator initialized")
    
    # Test queries
    test_queries = [
        "what is the weather??",
        "What's the weather today?",
        "What's the weather in New York?",
        "Calculate 25 * 4",
        "Hello, how are you?",
        "Calculate the ROI for a 10-acre organic farm",
        "Help me plan a farming strategy",
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 40)
        
        try:
            # Test routing decision
            routing = await coordinator.route_query(query)
            
            print(f"Mode: {routing.get('mode', 'UNKNOWN')}")
            print(f"Agents: {routing.get('agents', [])}")
            print(f"Parallel: {routing.get('parallel', False)}")
            print(f"Reasoning: {routing.get('reasoning', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Error testing query '{query}': {e}")
    
    print("\n🎉 Routing test completed!")

if __name__ == "__main__":
    print("🧪 Starting Routing Debug Test")
    
    # Check environment variables
    required_vars = ["LLM_API_KEY", "LLM_MODEL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please set them in your .env file")
        sys.exit(1)
    
    # Run test
    asyncio.run(test_routing())