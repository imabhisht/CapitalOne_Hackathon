#!/usr/bin/env python3
"""
Debug script to test imports for Streamlit app
"""
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

print("Python path:")
for path in sys.path:
    print(f"  {path}")

print("\nTesting imports...")

try:
    from services.chat_service import chat_service
    print("✅ Successfully imported chat_service")
except Exception as e:
    print(f"❌ Failed to import chat_service: {e}")
    import traceback
    traceback.print_exc()

try:
    from models.chat_request import ChatRequest
    print("✅ Successfully imported ChatRequest")
except Exception as e:
    print(f"❌ Failed to import ChatRequest: {e}")
    import traceback
    traceback.print_exc()

try:
    # Test creating a ChatRequest
    request = ChatRequest(message="test", user_id="test_user")
    print(f"✅ Successfully created ChatRequest: {request}")
except Exception as e:
    print(f"❌ Failed to create ChatRequest: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting chat service...")
try:
    # Test if chat service is available
    print(f"Chat service type: {type(chat_service)}")
    print("✅ Chat service is available")
except Exception as e:
    print(f"❌ Chat service error: {e}")
    import traceback
    traceback.print_exc()