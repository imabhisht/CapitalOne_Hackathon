#!/usr/bin/env python3
"""
Debug script to test MongoDB operations for chat messages.
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.infrastructure.mongo_service import mongo_service
from src.models.chat_session import ChatSession
from src.models.chat_message import ChatMessage

async def test_mongo_operations():
    """Test MongoDB operations for chat messages."""
    
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
    
    # Test creating a chat session
    try:
        test_user_id = "test_user_debug"
        chat_session = ChatSession(
            user_id=test_user_id,
            title="Debug Test Session"
        )
        print(f"✓ Created chat session: {chat_session.id}")
        
        # Add a human message
        human_msg = await chat_session.add_message(
            content="Hello, this is a test message",
            message_type="human",
            sync_to_db=True
        )
        print(f"✓ Added human message: {human_msg.id}")
        
        # Add an AI message
        ai_msg = await chat_session.add_message(
            content="Hello! This is a test AI response that should be saved to MongoDB.",
            message_type="ai",
            metadata={"generated_by": "debug_test", "model": "test"},
            sync_to_db=True
        )
        print(f"✓ Added AI message: {ai_msg.id}")
        
        # Verify messages were saved
        messages = await chat_session.get_messages(refresh=True)
        print(f"✓ Retrieved {len(messages)} messages from database")
        
        for i, msg in enumerate(messages):
            print(f"  Message {i+1}: {msg.message_type} - {msg.content[:50]}...")
        
        # Test direct database query
        db = mongo_service.get_collection("chat_messages")
        count = await db.count_documents({"session_id": chat_session.id})
        print(f"✓ Direct DB query shows {count} messages for session")
        
        # Clean up
        await chat_session.delete(delete_messages=True)
        print("✓ Cleaned up test data")
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mongo_operations())