#!/usr/bin/env python3
"""
Test script to verify tool adapter works correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.tools.registry import tool_registry

def test_tool_adapter():
    print("Testing ToolAdapter with LangChain tools...")
    
    # Get tools from registry
    location_tool = tool_registry.get_tool("get_location")
    weather_tool = tool_registry.get_tool("get_weather")
    
    print("\n=== Testing get_location tool ===")
    try:
        result = location_tool.invoke("")
        print(f"Success! Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== Testing get_weather tool ===")
    try:
        result = weather_tool.invoke("Mumbai")
        print(f"Success! Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== Testing get_weather with empty param ===")
    print("This test verifies the fix for empty parameter handling in LangChain tools")
    try:
        result = weather_tool.invoke("")
        print(f"Success! Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_tool_adapter()