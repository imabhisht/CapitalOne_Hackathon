#!/usr/bin/env python3
"""
Example usage of the Agricultural AI Advisor

This script demonstrates how to use the agricultural advisor system programmatically.
"""

import asyncio
import os
from src.chat_service import generate_complete_response, generate_streaming_response, create_session

async def example_complete_response():
    """Example of using complete response"""
    print("🌾 Example: Complete Response")
    print("=" * 50)
    
    # Create a session
    session_id = create_session()
    
    # Example query
    query = "When should I irrigate my wheat crop?"
    coordinates = {"lat": 40.7128, "lon": -74.0060}  # NYC coordinates
    
    print(f"Query: {query}")
    print(f"Session ID: {session_id}")
    print(f"Coordinates: {coordinates}")
    print()
    
    # Generate response
    response = await generate_complete_response(
        query, 
        session_id=session_id,
        coordinates=coordinates
    )
    
    print("Response:")
    print(response)
    print()

async def example_streaming_response():
    """Example of using streaming response"""
    print("🌾 Example: Streaming Response")
    print("=" * 50)
    
    # Create a session
    session_id = create_session()
    
    # Example query
    query = "My tomato plants have yellow leaves, what should I do?"
    coordinates = {"lat": 34.0522, "lon": -118.2437}  # LA coordinates
    
    print(f"Query: {query}")
    print(f"Session ID: {session_id}")
    print(f"Coordinates: {coordinates}")
    print()
    
    print("Response (streaming):")
    print("🤖 AI Advisor: ", end="", flush=True)
    
    # Generate streaming response
    async for chunk, is_complete in generate_streaming_response(
        query, 
        session_id=session_id,
        coordinates=coordinates
    ):
        if not is_complete:
            print(chunk, end="", flush=True)
        else:
            print()
            break
    
    print()

async def example_multiple_queries():
    """Example of multiple queries in a conversation"""
    print("🌾 Example: Multiple Queries Conversation")
    print("=" * 50)
    
    # Create a session for the conversation
    session_id = create_session()
    coordinates = {"lat": 41.8781, "lon": -87.6298}  # Chicago coordinates
    
    queries = [
        "What fertilizer should I use for rice?",
        "How do I control pests in my corn field?",
        "What's the weather forecast for my farm?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        
        response = await generate_complete_response(
            query, 
            session_id=session_id,
            coordinates=coordinates
        )
        
        print(f"Response: {response}")
    
    print()

async def example_error_handling():
    """Example of error handling"""
    print("🌾 Example: Error Handling")
    print("=" * 50)
    
    # Test with invalid coordinates
    session_id = create_session()
    query = "When should I irrigate my wheat crop?"
    invalid_coordinates = {"lat": 999, "lon": 999}  # Invalid coordinates
    
    print(f"Query: {query}")
    print(f"Invalid coordinates: {invalid_coordinates}")
    print()
    
    try:
        response = await generate_complete_response(
            query, 
            session_id=session_id,
            coordinates=invalid_coordinates
        )
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error handled: {str(e)}")
    
    print()

async def main():
    """Run all examples"""
    print("🚀 Agricultural AI Advisor - Example Usage")
    print("=" * 60)
    print()
    
    # Check if API keys are configured
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  Warning: GEMINI_API_KEY not set. Some features may not work.")
        print("   Set your API keys as environment variables:")
        print("   export GEMINI_API_KEY='your_key_here'")
        print("   export WEATHER_API_KEY='your_key_here'")
        print("   export EXA_API_KEY='your_key_here'")
        print()
    
    try:
        # Run examples
        await example_complete_response()
        await example_streaming_response()
        await example_multiple_queries()
        await example_error_handling()
        
        print("✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
        print("Make sure all dependencies are installed and API keys are configured.")

if __name__ == "__main__":
    asyncio.run(main()) 