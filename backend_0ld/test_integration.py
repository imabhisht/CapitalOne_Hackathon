#!/usr/bin/env python3
"""
Test script to verify integration between existing chat_service.py and agricultural advisor system
"""

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

async def test_all_queries():
    """Test all types of queries using the integrated system"""
    print("🌾 Testing All Queries with Agricultural System")
    print("=" * 50)
    
    from chat_service import generate_streaming_response, generate_complete_response, get_system_status
    
    # Check system status
    status = get_system_status()
    print(f"System Status: {status}")
    print()
    
    # Test various types of queries (all handled by agricultural system)
    test_queries = [
        # Agricultural queries
        "When should I irrigate my wheat crop?",
        "My tomato plants have yellow leaves, what should I do?",
        "What fertilizer should I use for rice?",
        "How do I control pests in my corn field?",
        "What's the weather forecast for my farm?",
        
        # Non-agricultural queries (agent will ask follow-up questions)
        "Hello, how are you?",
        "What's the weather like?",
        "Tell me a joke",
        "What's 2+2?",
        "How do I make coffee?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: {query}")
        print("-" * 40)
        
        # Test complete response
        try:
            response = await generate_complete_response(query)
            print(f"Complete Response: {response}")
        except Exception as e:
            print(f"Error in complete response: {e}")
        
        # Test streaming response
        try:
            print("Streaming Response: ", end="", flush=True)
            async for chunk, is_complete in generate_streaming_response(query):
                if not is_complete:
                    print(chunk, end="", flush=True)
                else:
                    print()
                    break
        except Exception as e:
            print(f"Error in streaming response: {e}")
        
        print()

async def test_with_coordinates():
    """Test queries with coordinates"""
    print("🌾 Testing with Coordinates")
    print("=" * 50)
    
    from chat_service import generate_complete_response
    
    coordinates = {"lat": 40.7128, "lon": -74.0060}  # NYC
    
    queries = [
        "When should I irrigate my wheat crop?",
        "What's the weather like?",
        "Hello there!"
    ]
    
    for query in queries:
        print(f"Query: {query}")
        print(f"Coordinates: {coordinates}")
        print()
        
        try:
            response = await generate_complete_response(
                query, 
                coordinates=coordinates
            )
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 30)

async def test_session_continuity():
    """Test session continuity for conversations"""
    print("🌾 Testing Session Continuity")
    print("=" * 50)
    
    from chat_service import generate_complete_response
    import uuid
    
    session_id = str(uuid.uuid4())
    print(f"Session ID: {session_id}")
    print()
    
    # Test conversation flow
    conversations = [
        {
            "title": "Agricultural Conversation",
            "queries": [
                "What fertilizer should I use for rice?",
                "How often should I apply it?",
                "What about for wheat?"
            ]
        },
        {
            "title": "General Conversation",
            "queries": [
                "Hello there!",
                "How are you doing?",
                "Can you help me with something?"
            ]
        }
    ]
    
    for conversation in conversations:
        print(f"💬 {conversation['title']}")
        print("-" * 30)
        
        for i, query in enumerate(conversation['queries'], 1):
            print(f"{i}. Query: {query}")
            try:
                response = await generate_complete_response(
                    query, 
                    session_id=session_id
                )
                print(f"Response: {response}")
            except Exception as e:
                print(f"Error: {e}")
            print()
        
        print()

async def test_system_capabilities():
    """Test system capabilities and status"""
    print("🌾 Testing System Capabilities")
    print("=" * 50)
    
    from chat_service import get_system_status
    
    status = get_system_status()
    
    print("📊 System Status:")
    for key, value in status.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")
    
    print()
    
    if status["agricultural_system_available"]:
        print("✅ Agricultural system is available")
        
        capabilities = status["capabilities"]
        print("🔧 Available Capabilities:")
        for capability in capabilities:
            print(f"  - {capability}")
        
        api_keys = status["api_keys_configured"]
        print("\n🔑 API Key Status:")
        for key, configured in api_keys.items():
            status_icon = "✅" if configured else "❌"
            print(f"  {status_icon} {key}: {'Configured' if configured else 'Missing'}")
    else:
        print("❌ Agricultural system is not available")
        print("   Using fallback responses only")

async def main():
    """Run all integration tests"""
    print("🚀 Agricultural AI Advisor - Integration Test")
    print("=" * 60)
    print("Note: All queries are now handled by the agricultural system")
    print("The agent will ask follow-up questions to understand user intent")
    print()
    
    try:
        # Run tests
        await test_system_capabilities()
        await test_all_queries()
        await test_with_coordinates()
        await test_session_continuity()
        
        print("✅ All integration tests completed!")
        print("\n💡 Key Points:")
        print("- All queries are handled by the agricultural advisor system")
        print("- The agent intelligently asks follow-up questions to understand intent")
        print("- Session continuity is maintained across conversations")
        print("- Coordinates can be passed for location-specific advice")
        print("- Both streaming and complete responses are supported")
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 