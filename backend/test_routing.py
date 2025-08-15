#!/usr/bin/env python3
"""
Test script to demonstrate smart routing functionality.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append('src')

# Load environment variables
load_dotenv()

from src.services.routing_service import routing_service
from src.models.chat_request import ChatRequest
from src.services.chat_service import chat_service

async def test_routing():
    """Test the routing service with various message types."""
    
    test_messages = [
        # Simple messages (should use small LLM)
        "Hello",
        "Hi there",
        "How are you?",
        "Thank you",
        "What time is it?",
        "Yes",
        "No",
        
        # Complex messages (should use main LLM)
        "Can you analyze the financial implications of a 30-year mortgage versus a 15-year mortgage?",
        "Write a Python function to calculate compound interest",
        "Explain the differences between machine learning and deep learning",
        "Help me create a budget plan for my small business",
        "What are the best investment strategies for retirement planning?",
        "Compare different credit card options for someone with good credit",
    ]
    
    print("🤖 Testing Smart Routing Service")
    print("=" * 50)
    
    for message in test_messages:
        print(f"\n📝 Message: '{message}'")
        
        # Get routing information
        routing_info = routing_service.get_routing_info(message)
        
        print(f"   📊 Classification: {routing_info['classification']}")
        print(f"   🎯 Confidence: {routing_info['confidence']:.2f}")
        print(f"   🔀 Use Small LLM: {routing_info['use_small_llm']}")
        print(f"   🤖 Selected Model: {routing_info['selected_model']}")
        print(f"   📏 Word Count: {routing_info['word_count']}")

async def test_chat_with_routing():
    """Test the chat service with routing enabled."""
    
    print("\n\n🚀 Testing Chat Service with Smart Routing")
    print("=" * 50)
    
    test_cases = [
        "Hello!",  # Should use small LLM
        "Can you help me understand compound interest calculations?"  # Should use main LLM
    ]
    
    for message in test_cases:
        print(f"\n💬 Testing: '{message}'")
        
        request = ChatRequest(
            message=message,
            user_id="test_user",
            session_id="test_session"
        )
        
        print("🔄 Response: ", end="", flush=True)
        
        try:
            full_response = ""
            async for chunk, is_complete in chat_service.generate_streaming_response(request):
                if not is_complete:
                    print(chunk, end="", flush=True)
                    full_response += chunk
                else:
                    print("\n✅ Complete!")
                    break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    print("🔧 Smart Routing Test Suite")
    print("=" * 50)
    
    # Test routing decisions
    asyncio.run(test_routing())
    
    # Test chat with routing (optional - requires working LLM setup)
    try:
        asyncio.run(test_chat_with_routing())
    except Exception as e:
        print(f"\n⚠️  Chat test skipped due to error: {e}")
        print("   Make sure your LLM credentials are configured correctly.")