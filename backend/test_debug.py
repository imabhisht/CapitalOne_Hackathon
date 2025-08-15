#!/usr/bin/env python3
"""
Debug script to trace the entire flow and identify where the static response is coming from.
"""

import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Set up logging to see all debug information
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.chat_request import ChatRequest
from src.services.chat_service import chat_service
from src.services.multi_agent_service import multi_agent_service

# Load environment variables
load_dotenv()

async def debug_flow():
    """Debug the entire flow to find where static responses come from."""
    
    print("🐛 Debug Flow Analysis")
    print("=" * 50)
    
    # Test query that should trigger iterative processing
    query = "what is the weather??"
    
    print(f"🔍 Testing query: '{query}'")
    print("-" * 40)
    
    # Check system configuration
    print("📋 System Configuration:")
    print(f"  - Chat service use_multi_agent: {chat_service.use_multi_agent}")
    print(f"  - Chat service use_smart_routing: {chat_service.use_smart_routing}")
    print(f"  - Multi-agent service available: {multi_agent_service.is_available()}")
    
    if multi_agent_service.is_available():
        print(f"  - Coordinator has iterative_agent: {hasattr(multi_agent_service.coordinator, 'iterative_agent')}")
        if hasattr(multi_agent_service.coordinator, 'iterative_agent'):
            print(f"  - Max iterations: {multi_agent_service.coordinator.iterative_agent.max_iterations}")
    
    print("\n🔄 Testing routing decision...")
    try:
        if multi_agent_service.is_available():
            routing = await multi_agent_service.coordinator.route_query(query)
            print(f"  - Routing result: {routing}")
        else:
            print("  - ❌ Multi-agent service not available for routing test")
    except Exception as e:
        print(f"  - ❌ Routing error: {e}")
    
    print("\n💬 Testing chat service flow...")
    try:
        request = ChatRequest(message=query)
        
        print("  - Chat service response:")
        response_chunks = []
        async for chunk, is_complete in chat_service.generate_streaming_response(request):
            if not is_complete:
                response_chunks.append(chunk)
                print(chunk, end="", flush=True)
            else:
                print(f"\n  - ✅ Chat service complete")
                break
        
        full_response = "".join(response_chunks)
        print(f"\n  - Full response length: {len(full_response)} characters")
        print(f"  - Response preview: '{full_response[:100]}...'")
        
        # Check if this looks like a static response
        if "get_location result:" in full_response:
            print("  - ⚠️  DETECTED STATIC RESPONSE - This is the issue!")
        else:
            print("  - ✅ Response appears dynamic")
            
    except Exception as e:
        print(f"  - ❌ Chat service error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Starting Debug Flow Analysis")
    
    # Check environment variables
    if not os.getenv("LLM_API_KEY"):
        print("❌ LLM_API_KEY not set")
        sys.exit(1)
    
    # Run debug
    asyncio.run(debug_flow())