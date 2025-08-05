#!/usr/bin/env python3
"""
Simple test script for the Agricultural AI Advisor

This script tests the basic functionality without requiring API keys.
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from src.config import Config
        print("✅ Config imported successfully")
        
        from src.database import chat_storage
        print("✅ Database imported successfully")
        
        from src.llm_client import gemini_client
        print("✅ LLM client imported successfully")
        
        from src.tools import AGRICULTURAL_TOOLS
        print("✅ Tools imported successfully")
        
        from src.agent import agricultural_system
        print("✅ Agent imported successfully")
        
        from src.chat_service import agricultural_chat_service
        print("✅ Chat service imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration validation"""
    print("\n🧪 Testing configuration...")
    
    try:
        from src.config import Config
        
        # Test config validation
        is_valid = Config.validate_config()
        if is_valid:
            print("✅ Configuration is valid")
        else:
            print("⚠️  Configuration has warnings (API keys missing)")
        
        # Test config values
        print(f"✅ Model: {Config.GEMINI_MODEL}")
        print(f"✅ Max tokens: {Config.MAX_TOKENS}")
        print(f"✅ Temperature: {Config.TEMPERATURE}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_tools():
    """Test tool definitions"""
    print("\n🧪 Testing tools...")
    
    try:
        from src.tools import AGRICULTURAL_TOOLS
        
        expected_tools = [
            "get_weather_by_coords",
            "search_agricultural_knowledge", 
            "calculate_irrigation_schedule",
            "pest_identification_guide",
            "fertilizer_recommendations"
        ]
        
        for tool_name in expected_tools:
            if tool_name in AGRICULTURAL_TOOLS:
                print(f"✅ Tool '{tool_name}' found")
            else:
                print(f"❌ Tool '{tool_name}' missing")
                return False
        
        print(f"✅ All {len(expected_tools)} tools are defined")
        return True
        
    except Exception as e:
        print(f"❌ Tools error: {e}")
        return False

async def test_basic_functionality():
    """Test basic functionality without API keys"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from src.chat_service import create_session
        
        # Test session creation
        session_id = create_session()
        print(f"✅ Session created: {session_id}")
        
        # Test that session ID is valid UUID format
        import uuid
        try:
            uuid.UUID(session_id)
            print("✅ Session ID is valid UUID")
        except ValueError:
            print("❌ Session ID is not valid UUID")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality error: {e}")
        return False

def test_agent_structure():
    """Test agent structure and workflow"""
    print("\n🧪 Testing agent structure...")
    
    try:
        from src.agent import create_agricultural_advisor_agent
        
        # Create agent
        agent = create_agricultural_advisor_agent()
        print("✅ Agent created successfully")
        
        # Check agent properties
        if hasattr(agent, 'nodes'):
            print(f"✅ Agent has {len(agent.nodes)} nodes")
        else:
            print("❌ Agent missing nodes attribute")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Agent structure error: {e}")
        return False

def test_database_connection():
    """Test database connection (without actual connection)"""
    print("\n🧪 Testing database setup...")
    
    try:
        from src.database import ChatStorage
        
        # Test ChatStorage class
        storage = ChatStorage()
        print("✅ ChatStorage class instantiated")
        
        # Test methods exist
        if hasattr(storage, 'save_message'):
            print("✅ save_message method exists")
        else:
            print("❌ save_message method missing")
            return False
            
        if hasattr(storage, 'get_chat_history'):
            print("✅ get_chat_history method exists")
        else:
            print("❌ get_chat_history method missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Agricultural AI Advisor - System Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Tools", test_tools),
        ("Basic Functionality", test_basic_functionality),
        ("Agent Structure", test_agent_structure),
        ("Database Setup", test_database_connection)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
            else:
                print(f"❌ {test_name} failed")
                
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Set your API keys as environment variables")
        print("2. Run: python src/main.py interactive")
        print("3. Or run: python example_usage.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1) 