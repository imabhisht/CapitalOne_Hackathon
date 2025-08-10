"""
Test script for conversation history functionality.
"""

import asyncio
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

from src.llm.gemini_llm import GeminiLLM
from src.agents.langraph_agent import LangGraphAgent

async def test_conversation_history():
    """Test the agent with conversation history."""
    
    # Initialize LLM and Agent
    llm = GeminiLLM(
        model="gemini-2.0-flash-exp",
        api_key=os.getenv("GEMINI_API_KEY")
    )
    
    agent = LangGraphAgent(llm)
    
    # Simulate conversation history
    conversation_history = [
        HumanMessage(content="My name is John"),
        AIMessage(content="Nice to meet you, John! How can I help you today?"),
        HumanMessage(content="I live in New York"),
        AIMessage(content="That's great! New York is a wonderful city. What would you like to know?")
    ]
    
    # Test query that should reference the history
    query = "What's my name and where do I live?"
    
    print(f"Query: {query}")
    print(f"Conversation history: {len(conversation_history)} messages")
    print("="*50)
    
    try:
        # Test with conversation history
        response_parts = []
        async for chunk, is_complete in agent.stream_invoke(query, conversation_history):
            if not is_complete:
                response_parts.append(chunk)
                print(chunk, end='', flush=True)
            else:
                print("\n")
                break
        
        full_response = ''.join(response_parts).strip()
        print(f"\nFull Response: {full_response}")
        
        # Check if the response contains expected information
        if "John" in full_response and "New York" in full_response:
            print("✅ SUCCESS: Agent correctly used conversation history!")
        else:
            print("❌ FAILED: Agent did not use conversation history properly")
            print(f"Expected: Should mention 'John' and 'New York'")
            print(f"Got: {full_response}")
        
    except Exception as e:
        print(f"Error: {e}")

async def test_without_history():
    """Test the same query without conversation history."""
    
    # Initialize LLM and Agent
    llm = GeminiLLM(
        model="gemini-2.0-flash-exp",
        api_key=os.getenv("GEMINI_API_KEY")
    )
    
    agent = LangGraphAgent(llm)
    
    # Test query without history
    query = "What's my name and where do I live?"
    
    print(f"\n{'='*50}")
    print("Testing WITHOUT conversation history:")
    print(f"Query: {query}")
    print("="*50)
    
    try:
        response_parts = []
        async for chunk, is_complete in agent.stream_invoke(query, None):
            if not is_complete:
                response_parts.append(chunk)
                print(chunk, end='', flush=True)
            else:
                print("\n")
                break
        
        full_response = ''.join(response_parts).strip()
        print(f"\nFull Response: {full_response}")
        
        # This should indicate the agent doesn't know
        if "don't know" in full_response.lower() or "not provided" in full_response.lower():
            print("✅ SUCCESS: Agent correctly indicated lack of information!")
        else:
            print("ℹ️  INFO: Agent response without history context")
        
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Run all conversation history tests."""
    print("Testing LangGraph Agent Conversation History")
    print("="*60)
    
    # Test with conversation history
    await test_conversation_history()
    
    # Test without conversation history for comparison
    await test_without_history()
    
    print("\n" + "="*60)
    print("All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())