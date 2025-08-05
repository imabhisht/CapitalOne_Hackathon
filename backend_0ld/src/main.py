#!/usr/bin/env python3
"""
Agricultural AI Advisor - Main Entry Point

This script provides a simple command-line interface for testing the agricultural advisor system.
"""

import asyncio
import sys
import logging
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the agricultural advisor system
try:
    from .chat_service import generate_complete_response, create_session
    from .config import Config
except ImportError:
    # Fallback for direct execution
    from chat_service import generate_complete_response, create_session
    from config import Config

async def interactive_chat():
    """Interactive chat interface for testing"""
    print("🌾 Agricultural AI Advisor 🌾")
    print("=" * 50)
    print("Type 'quit' to exit, 'help' for available commands")
    print("=" * 50)
    
    # Create a new session
    session_id = create_session()
    print(f"Session ID: {session_id}")
    print()
    
    # Optional: Get coordinates for weather data
    coordinates = None
    try:
        use_coordinates = input("Would you like to provide coordinates for weather data? (y/n): ").lower().strip()
        if use_coordinates == 'y':
            lat = float(input("Enter latitude (e.g., 40.7128): "))
            lon = float(input("Enter longitude (e.g., -74.0060): "))
            coordinates = {"lat": lat, "lon": lon}
            print(f"Using coordinates: {lat}, {lon}")
    except (ValueError, KeyboardInterrupt):
        print("Using default coordinates (New York City)")
        coordinates = {"lat": 40.7128, "lon": -74.0060}
    
    print()
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif not user_input:
                continue
            
            # Generate response
            print("🤖 AI Advisor: ", end="", flush=True)
            response = await generate_complete_response(
                user_input, 
                session_id=session_id,
                coordinates=coordinates
            )
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            logger.error(f"Error in interactive chat: {e}")
            print(f"Error: {str(e)}")
            print()

def print_help():
    """Print help information"""
    print("\n📋 Available Commands:")
    print("- 'quit', 'exit', 'q': Exit the chat")
    print("- 'help': Show this help message")
    print("\n🌱 Example Questions:")
    print("- 'When should I irrigate my wheat crop?'")
    print("- 'My tomato plants have yellow leaves, what should I do?'")
    print("- 'What fertilizer should I use for rice?'")
    print("- 'How do I control pests in my corn field?'")
    print("- 'What's the weather forecast for my farm?'")
    print()

async def test_specific_queries():
    """Test specific agricultural queries"""
    print("🧪 Testing Agricultural AI Advisor")
    print("=" * 50)
    
    session_id = create_session()
    coordinates = {"lat": 40.7128, "lon": -74.0060}  # NYC coordinates
    
    test_queries = [
        "When should I irrigate my wheat crop?",
        "My tomato plants have yellow leaves, what should I do?",
        "What fertilizer should I use for rice?",
        "How do I control pests in my corn field?",
        "What's the weather forecast for my farm?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: {query}")
        print("-" * 40)
        
        try:
            response = await generate_complete_response(
                query, 
                session_id=session_id,
                coordinates=coordinates
            )
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print()

async def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            await test_specific_queries()
        elif command == "interactive":
            await interactive_chat()
        else:
            print("Usage: python main.py [test|interactive]")
            print("  test: Run predefined test queries")
            print("  interactive: Start interactive chat")
    else:
        # Default to interactive mode
        await interactive_chat()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye! 👋")
    except Exception as e:
        logger.error(f"Main execution error: {e}")
        print(f"Error: {str(e)}")
        sys.exit(1) 