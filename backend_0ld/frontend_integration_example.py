#!/usr/bin/env python3
"""
Example showing how frontend can integrate with the updated chat_service.py

This demonstrates the seamless integration where ALL queries are handled by the 
agricultural advisor system, which intelligently asks follow-up questions to understand user intent.
"""

import asyncio
import json
from chat_service import generate_streaming_response, generate_complete_response, get_system_status

async def simulate_frontend_chat():
    """Simulate frontend chat interface"""
    print("🌾 Frontend Integration Example")
    print("=" * 50)
    print("This simulates how a frontend would interact with the integrated chat service")
    print("Note: ALL queries are handled by the agricultural advisor system")
    print()
    
    # Check system status
    status = get_system_status()
    print("📊 System Status:")
    print(json.dumps(status, indent=2))
    print()
    
    # Simulate user conversations
    conversations = [
        {
            "title": "Agricultural Query - Irrigation",
            "messages": [
                "When should I irrigate my wheat crop?",
                "How much water should I use?",
                "What if it rains tomorrow?"
            ]
        },
        {
            "title": "Agricultural Query - Pest Control", 
            "messages": [
                "My tomato plants have yellow leaves",
                "What pests could cause this?",
                "How do I treat it naturally?"
            ]
        },
        {
            "title": "General Query - Agent will ask follow-up questions",
            "messages": [
                "Hello, how are you?",
                "I need some help",
                "What can you do for me?"
            ]
        },
        {
            "title": "Weather Query - Agent will understand context",
            "messages": [
                "What's the weather like?",
                "Will it rain today?",
                "How does this affect my crops?"
            ]
        }
    ]
    
    for conversation in conversations:
        print(f"💬 {conversation['title']}")
        print("-" * 40)
        
        session_id = None  # Let the system generate one
        
        for i, message in enumerate(conversation['messages'], 1):
            print(f"\n👤 User {i}: {message}")
            
            # Simulate frontend calling the streaming response
            print("🤖 AI: ", end="", flush=True)
            
            try:
                async for chunk, is_complete in generate_streaming_response(
                    message, 
                    session_id=session_id
                ):
                    if not is_complete:
                        print(chunk, end="", flush=True)
                    else:
                        print()
                        break
                        
            except Exception as e:
                print(f"Error: {e}")
        
        print()

async def simulate_api_endpoint():
    """Simulate API endpoint usage"""
    print("🌾 API Endpoint Simulation")
    print("=" * 50)
    print("This shows how an API endpoint would use the integrated service")
    print("All queries are handled by the agricultural advisor system")
    print()
    
    # Simulate various API requests
    api_requests = [
        {
            "message": "When should I irrigate my wheat crop?",
            "session_id": "user_session_123",
            "coordinates": {"lat": 40.7128, "lon": -74.0060}
        },
        {
            "message": "Hello, how are you?",
            "session_id": "user_session_456"
        },
        {
            "message": "What's the weather like?",
            "session_id": "user_session_789",
            "coordinates": {"lat": 34.0522, "lon": -118.2437}
        }
    ]
    
    for i, api_request in enumerate(api_requests, 1):
        print(f"📤 API Request {i}: {json.dumps(api_request, indent=2)}")
        print()
        
        # Simulate complete response endpoint
        try:
            complete_response = await generate_complete_response(
                api_request["message"],
                session_id=api_request.get("session_id"),
                coordinates=api_request.get("coordinates")
            )
            
            api_response = {
                "status": "success",
                "response": complete_response,
                "session_id": api_request.get("session_id"),
                "query_type": "handled_by_agricultural_system"
            }
            
            print(f"📥 API Response {i}: {json.dumps(api_response, indent=2)}")
            
        except Exception as e:
            error_response = {
                "status": "error",
                "error": str(e),
                "session_id": api_request.get("session_id")
            }
            print(f"📥 API Error Response {i}: {json.dumps(error_response, indent=2)}")
        
        print("-" * 50)

async def simulate_streaming_endpoint():
    """Simulate streaming API endpoint"""
    print("🌾 Streaming API Endpoint Simulation")
    print("=" * 50)
    print("This shows how a streaming API endpoint would work")
    print("All queries are handled by the agricultural advisor system")
    print()
    
    # Simulate streaming requests
    streaming_requests = [
        {
            "message": "My tomato plants have yellow leaves, what should I do?",
            "session_id": "user_session_456"
        },
        {
            "message": "Hello there!",
            "session_id": "user_session_789"
        }
    ]
    
    for i, streaming_request in enumerate(streaming_requests, 1):
        print(f"📤 Streaming Request {i}: {json.dumps(streaming_request, indent=2)}")
        print()
        
        # Simulate streaming response
        print(f"📥 Streaming Response {i}:")
        try:
            response_chunks = []
            async for chunk, is_complete in generate_streaming_response(
                streaming_request["message"],
                session_id=streaming_request["session_id"]
            ):
                if not is_complete:
                    response_chunks.append(chunk)
                    print(f"Chunk: {repr(chunk)}")
                else:
                    print("Stream complete")
                    break
            
            final_response = "".join(response_chunks)
            print(f"\nFinal Response {i}: {final_response}")
            
        except Exception as e:
            print(f"Streaming Error {i}: {e}")
        
        print("-" * 50)

async def simulate_conversation_flow():
    """Simulate a natural conversation flow"""
    print("🌾 Natural Conversation Flow Simulation")
    print("=" * 50)
    print("This shows how the agent handles different types of queries in a conversation")
    print()
    
    session_id = "conversation_session_123"
    
    conversation_flow = [
        "Hello!",
        "I'm a farmer and I need some help",
        "My wheat crop isn't growing well",
        "The leaves are turning yellow",
        "What should I do?",
        "Thank you for the advice!"
    ]
    
    print(f"Session ID: {session_id}")
    print()
    
    for i, message in enumerate(conversation_flow, 1):
        print(f"👤 User {i}: {message}")
        print("🤖 AI: ", end="", flush=True)
        
        try:
            async for chunk, is_complete in generate_streaming_response(
                message, 
                session_id=session_id
            ):
                if not is_complete:
                    print(chunk, end="", flush=True)
                else:
                    print()
                    break
        except Exception as e:
            print(f"Error: {e}")
        
        print()

async def main():
    """Run all frontend integration examples"""
    print("🚀 Frontend Integration Examples")
    print("=" * 60)
    print("Note: ALL queries are now handled by the agricultural advisor system")
    print("The agent intelligently asks follow-up questions to understand user intent")
    print()
    
    try:
        await simulate_frontend_chat()
        await simulate_api_endpoint()
        await simulate_streaming_endpoint()
        await simulate_conversation_flow()
        
        print("✅ All frontend integration examples completed!")
        print("\n💡 Key Points:")
        print("- ALL queries are handled by the agricultural advisor system")
        print("- The agent intelligently asks follow-up questions to understand intent")
        print("- No query filtering or routing logic needed")
        print("- Session continuity is maintained across conversations")
        print("- Coordinates can be passed for location-specific advice")
        print("- Both streaming and complete responses are supported")
        print("- Natural conversation flow with intelligent responses")
        
    except Exception as e:
        print(f"❌ Frontend integration error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 