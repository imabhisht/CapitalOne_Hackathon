#!/usr/bin/env python3
"""
Test script to verify API connection and chat functionality
"""
import requests
import json

API_BASE_URL = "http://localhost:5050"

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print(f"Health check status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Health check failed: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_chat():
    """Test the chat endpoint"""
    try:
        request_data = {
            "message": "Hello, this is a test message",
            "user_id": "test_user_123"
        }
        
        print(f"\nSending chat request: {request_data}")
        
        response = requests.post(
            f"{API_BASE_URL}/chat/stream",
            json=request_data,
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=30
        )
        
        print(f"Chat response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Chat request successful")
            print("Response chunks:")
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        try:
                            data = json.loads(line_str[6:])
                            content = data.get('content', '')
                            is_complete = data.get('is_complete', False)
                            
                            if content:
                                full_response += content
                                print(f"  Chunk: {repr(content)}")
                            
                            if is_complete:
                                print("  ✅ Response complete")
                                break
                                
                        except json.JSONDecodeError as e:
                            print(f"  ❌ JSON decode error: {e}")
                            print(f"  Raw line: {repr(line_str)}")
            
            print(f"\nFull response: {repr(full_response)}")
            return True
        else:
            print(f"❌ Chat request failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat request error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing API connection...")
    print(f"API Base URL: {API_BASE_URL}")
    
    # Test health endpoint
    if test_health():
        # Test chat endpoint
        test_chat()
    else:
        print("\n💡 Make sure to start the FastAPI server first:")
        print("   python main.py")
        print("   or")
        print("   python app.py")