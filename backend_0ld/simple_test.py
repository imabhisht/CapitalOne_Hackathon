#!/usr/bin/env python3
"""
Simple test to verify the chat service is working properly
"""

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

async def test_chat_service():
    """Test the chat service"""
    print("🧪 Testing Chat Service")
    print("=" * 40)
    
    try:
        from chat_service import generate_complete_response, get_system_status
        
        # Check system status
        status = get_system_status()
        print(f"System Status: {status}")
        print()
        
        # Test a simple query
        query = "Hello, how are you?"
        print(f"Query: {query}")
        
        response = await generate_complete_response(query)
        print(f"Response: {response}")
        
        print("\n✅ Chat service is working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat_service()) 