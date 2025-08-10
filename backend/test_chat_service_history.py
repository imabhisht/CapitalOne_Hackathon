"""
Test script for ChatService conversation history functionality.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.models.chat_request import ChatRequest
from src.services.chat_service import ChatService

async def test_chat_service_history():
    """Test the ChatService with conversation history."""
    
    chat_service = ChatService()
    
    # Test user and session
    user_id = "test_user_123"
    session_id = None  # Will be created automatically
    
    print("Testing ChatService conversation history...")
    print("="*60)
    
    # First message - introduce name
    print("\n1. First message: Introducing name")
    request1 = ChatRequest(
        message="Hi, my name is Alice and I live in San Francisco",
        user_id=user_id,
        session_id=session_id
    )
    
    response_parts = []
    async for chunk, is_complete in chat_service.generate_streaming_response(request1):
        if not is_complete:
            response_parts.append(chunk)
            print(chunk, end='', flush=True)
        else:
            print("\n")
            break
    
    response1 = ''.join(response_parts).strip()
    print(f"Response 1: {response1}")
    
    # Get the session_id from the chat_session (we need to access it somehow)
    # For now, let's simulate having a session_id
    session_id = "test_session_456"  # In real implementation, this would come from the response
    
    print("\n" + "-"*60)
    
    # Second message - ask about hobby
    print("\n2. Second message: Mentioning hobby")
    request2 = ChatRequest(
        message="I love hiking and photography",
        user_id=user_id,
        session_id=session_id
    )
    
    response_parts = []
    async for chunk, is_complete in chat_service.generate_streaming_response(request2):
        if not is_complete:
            response_parts.append(chunk)
            print(chunk, end='', flush=True)
        else:
            print("\n")
            break
    
    response2 = ''.join(response_parts).strip()
    print(f"Response 2: {response2}")
    
    print("\n" + "-"*60)
    
    # Third message - test if it remembers previous context
    print("\n3. Third message: Testing memory")
    request3 = ChatRequest(
        message="What's my name and where do I live? What are my hobbies?",
        user_id=user_id,
        session_id=session_id
    )
    
    response_parts = []
    async for chunk, is_complete in chat_service.generate_streaming_response(request3):
        if not is_complete:
            response_parts.append(chunk)
            print(chunk, end='', flush=True)
        else:
            print("\n")
            break
    
    response3 = ''.join(response_parts).strip()
    print(f"Response 3: {response3}")
    
    print("\n" + "="*60)
    print("Test completed!")
    
    # Check if the response contains the expected information
    if "Alice" in response3 and "San Francisco" in response3:
        print("✅ SUCCESS: Agent remembered name and location!")
    else:
        print("❌ FAILED: Agent did not remember name and location")
    
    if "hiking" in response3.lower() or "photography" in response3.lower():
        print("✅ SUCCESS: Agent remembered hobbies!")
    else:
        print("❌ FAILED: Agent did not remember hobbies")

if __name__ == "__main__":
    asyncio.run(test_chat_service_history())