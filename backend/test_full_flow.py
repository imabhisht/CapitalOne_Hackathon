#!/usr/bin/env python3
"""
Test the full flow from chat service to iterative agent.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.chat_request import ChatRequest
from src.services.chat_service import chat_service
from src.services.multi_agent_service import multi_agent_service

# Load environment variables
load_dotenv()

async def test_full_flow():
    """Test the complete flow from chat service to iterative agent."""
    
    print("🔄 Testing Full Flow: Chat Service → Multi-Agent → Iterative Agent")
    print("=" * 70)
    
    # Test query
    query = "what is the weather??"
    
    print(f"🔍 Testing query: '{query}'")
    print("-" * 50)
    
    # Check multi-agent service availability
    print(f"Multi-agent service available: {multi_agent_service.is_available()}")
    print(f"Chat service use_multi_agent: {chat_service.use_multi_agent}")
    
    if multi_agent_service.is_available():
        print(f"Coordinator available: {hasattr(multi_agent_service.coordinator, 'iterative_agent')}")
        if hasattr(multi_agent_service.coordinator, 'iterative_agent'):
            print(f"Iterative agent max iterations: {multi_agent_service.coordinator.iterative_agent.max_iterations}")
    
    print("\n📡 Testing routing decision...")
    try:
        if multi_agent_service.is_available():
            routing = await multi_agent_service.coordinator.route_query(query)
            print(f"Routing decision: {routing}")
        else:
            print("❌ Multi-agent service not available")
    except Exception as e:
        print(f"❌ Error in routing: {e}")
    
    print("\n🎯 Testing direct multi-agent streaming...")
    try:
        request = ChatRequest(message=query)
        
        print("Response:")
        async for chunk, is_complete in multi_agent_service.generate_streaming_response(request):
            if not is_complete:
                print(chunk, end="", flush=True)
            else:
                print("\n✅ Streaming complete")
                break
                
    except Exception as e:
        print(f"❌ Error in multi-agent streaming: {e}")
    
    print("\n🔄 Testing full chat service flow...")
    try:
        request = ChatRequest(message=query)
        
        print("Response:")
        async for chunk, is_complete in chat_service.generate_streaming_response(request):
            if not is_complete:
                print(chunk, end="", flush=True)
            else:
                print("\n✅ Chat service streaming complete")
                break
                
    except Exception as e:
        print(f"❌ Error in chat service: {e}")

if __name__ == "__main__":
    print("🧪 Starting Full Flow Test")
    
    # Check environment variables
    required_vars = ["LLM_API_KEY", "LLM_MODEL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please set them in your .env file")
        sys.exit(1)
    
    # Run test
    asyncio.run(test_full_flow())