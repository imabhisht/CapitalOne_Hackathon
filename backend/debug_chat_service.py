#!/usr/bin/env python3
"""
Debug script to test the chat service streaming and saving logic.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.services.chat_service import chat_service
from src.models.chat_request import ChatRequest
from src.infrastructure.mongo_service import mongo_service

async def test_chat_service():
    """Test the chat service streaming and saving."""
    
    # Initialize MongoDB
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        print("ERROR: MONGODB_URI environment variable not set")
        return
    
    try:
        await mongo_service.initialize(mongodb_uri)
        print("✓ MongoDB initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize MongoDB: {e}")
        return
    
    # Create a test chat request
    request = ChatRequest(
        message="Hello, can you tell me about the weather?",
        user_id="debug_test_user",
        language_type="en"
    )
    
    print(f"Testing chat service with message: '{request.message}'")
    print("Streaming response:")
    
    accumulated_debug = ""
    chunk_count = 0
    
    try:
        async for chunk, is_complete in chat_service.generate_streaming_response(request):
            chunk_count += 1
            print(f"Chunk {chunk_count}: '{chunk}' (complete: {is_complete})")
            
            if not is_complete:
                accumulated_debug += chunk
            
            if is_complete:
                print(f"\n✓ Streaming complete after {chunk_count} chunks")
                print(f"✓ Accumulated response length: {len(accumulated_debug)}")
                print(f"✓ Accumulated response preview: '{accumulated_debug[:100]}...'")
                break
        
        # Wait a moment for any async operations to complete
        await asyncio.sleep(1)
        
        # Check if messages were saved
        print("\nChecking saved messages...")
        db = mongo_service.get_collection("chat_messages")
        
        # Find messages for this user
        messages = []
        async for msg in db.find({"session_id": {"$exists": True}}).sort("created_at", -1).limit(20):
            messages.append(msg)
        
        print(f"All recent messages:")
        for i, msg in enumerate(messages):
            print(f"  Message {i+1}: {msg['message_type']} - Session: {msg['session_id'][:8]}... - {msg['content'][:60]}...")
        
        # Look specifically for our test messages
        test_messages = []
        for msg in messages:
            if msg.get("content") and ("Hello, can you tell me about the weather?" in msg.get("content", "") or 
                                     "I can definitely help with that!" in msg.get("content", "")):
                test_messages.append(msg)
        
        print(f"Found {len(test_messages)} test messages:")
        for i, msg in enumerate(test_messages):
            print(f"  Test Message {i+1}: {msg['message_type']} - {msg['content'][:100]}...")
        
        # Clean up - find and delete test messages
        await db.delete_many({"content": {"$regex": "Hello, can you tell me about the weather?"}})
        print("✓ Cleaned up test messages")
        
    except Exception as e:
        print(f"✗ Error during chat service test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat_service())