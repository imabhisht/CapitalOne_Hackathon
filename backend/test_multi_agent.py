#!/usr/bin/env python3
"""
Test script for the multi-agent system.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from src.services.multi_agent_service import multi_agent_service
from src.models.chat_request import ChatRequest

async def test_multi_agent_system():
    """Test the multi-agent system with various queries."""
    
    print("🤖 Testing Multi-Agent System")
    print("=" * 50)
    
    # Check if service is available
    if not multi_agent_service.is_available():
        print("❌ Multi-agent service is not available. Check your LLM_API_KEY and LLM_BASE_URL.")
        return
    
    print("✅ Multi-agent service is available")
    
    # Get agent information
    agent_info = multi_agent_service.get_agent_info()
    print(f"\n📋 Available Agents:")
    for name, info in agent_info.items():
        print(f"  • {info['name']}: {info['description']}")
    
    # Test queries for different agents
    test_queries = [
        {
            "query": "What's the weather like for farming today?",
            "expected_agent": "weather"
        },
        {
            "query": "How can I improve my organic tomato yield?",
            "expected_agent": "organic_farming"
        },
        {
            "query": "Calculate the ROI if I invest $10,000 and get $12,000 back",
            "expected_agent": "financial"
        },
        {
            "query": "What's the best organic fertilizer for vegetables and how much profit can I expect?",
            "expected_agent": "multiple (organic_farming + financial)"
        },
        {
            "query": "Hello, how are you today?",
            "expected_agent": "general"
        }
    ]
    
    print(f"\n🧪 Running {len(test_queries)} test queries...")
    print("=" * 50)
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {test['query']}")
        print(f"   Expected: {test['expected_agent']}")
        print("   Response: ", end="")
        
        try:
            request = ChatRequest(message=test['query'])
            
            # Test streaming response
            response_parts = []
            async for chunk, is_complete in multi_agent_service.generate_streaming_response(request):
                if not is_complete:
                    print(chunk, end="", flush=True)
                    response_parts.append(chunk)
                else:
                    print("\n")
                    break
            
            # Check if we got a reasonable response
            full_response = "".join(response_parts)
            if len(full_response.strip()) > 10:
                print("   ✅ Response received")
            else:
                print("   ⚠️  Short response")
                
        except Exception as e:
            print(f"\n   ❌ Error: {e}")
        
        print("-" * 30)
    
    print("\n🎉 Multi-agent system testing completed!")

async def test_agent_routing():
    """Test the agent routing logic specifically."""
    
    print("\n🎯 Testing Agent Routing Logic")
    print("=" * 50)
    
    if not multi_agent_service.is_available():
        print("❌ Multi-agent service not available")
        return
    
    coordinator = multi_agent_service.coordinator
    
    routing_tests = [
        "What's the weather?",
        "How to grow organic tomatoes?",
        "Calculate 15% of $50,000",
        "Best organic fertilizer and expected profit margins",
        "Hello there!"
    ]
    
    for query in routing_tests:
        print(f"\nQuery: {query}")
        try:
            routing = await coordinator.route_query(query)
            print(f"  Agents: {routing['agents']}")
            print(f"  Parallel: {routing['parallel']}")
            print(f"  Reasoning: {routing['reasoning']}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    print("Starting multi-agent system tests...")
    
    # Run the tests
    asyncio.run(test_multi_agent_system())
    asyncio.run(test_agent_routing())
    
    print("\nAll tests completed! 🚀")