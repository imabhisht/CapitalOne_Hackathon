#!/usr/bin/env python3
"""
Test script for the Iterative Agent functionality.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend src directory to the Python path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from src.agents.iterative_agent import IterativeAgent
from src.llm.openai_compatible_llm import OpenAICompatibleLLM

async def test_iterative_agent():
    """Test the iterative agent with various queries."""
    
    print("🧪 Testing Iterative Agent")
    print("=" * 50)
    
    # Initialize LLM
    try:
        llm = OpenAICompatibleLLM(
            model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
        )
        print("✅ LLM initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize LLM: {e}")
        return
    
    # Create iterative agent
    agent = IterativeAgent(llm, max_iterations=5)
    print(f"✅ Iterative agent created (max_iterations: {agent.max_iterations})")
    
    # Test queries
    test_queries = [
        "What is 25 * 4 + 10?",
        "What's the weather today and should I plant crops?",  # Tests location detection + weather + analysis
        "Calculate the area of a circle with radius 5 and tell me if it's suitable for farming"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 50)
        
        try:
            # Test streaming response
            total_content = ""
            async for chunk, is_complete, step_info in agent.stream_process_iteratively(query):
                if not is_complete:
                    print(chunk, end="", flush=True)
                    total_content += chunk
                else:
                    if step_info:
                        iterations = step_info.get("total_iterations", 0)
                        if step_info.get("final"):
                            print(f"\n✅ Completed in {iterations} iterations")
                        elif step_info.get("error"):
                            print(f"\n❌ Error occurred after {iterations} iterations")
            
            print("\n" + "=" * 50)
            
        except Exception as e:
            print(f"\n❌ Error during test {i}: {e}")
    
    print("\n🎉 Iterative agent testing completed!")

async def test_non_streaming():
    """Test non-streaming functionality."""
    
    print("\n🧪 Testing Non-Streaming Mode")
    print("=" * 50)
    
    try:
        llm = OpenAICompatibleLLM(
            model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL")
        )
        
        agent = IterativeAgent(llm, max_iterations=3)
        
        query = "Calculate 15 + 25 and explain the result"
        print(f"Query: {query}")
        print("-" * 30)
        
        final_answer, iteration_steps = await agent.process_iteratively(query)
        
        print(f"Final Answer: {final_answer}")
        print(f"Total Steps: {len(iteration_steps)}")
        
        for step in iteration_steps:
            print(f"\nStep {step.step_number}:")
            print(f"  Thought: {step.thought}")
            if step.action:
                print(f"  Action: {step.action}")
                print(f"  Input: {step.action_input}")
            if step.observation:
                print(f"  Observation: {step.observation}")
            print(f"  Final: {step.is_final}")
        
    except Exception as e:
        print(f"❌ Error in non-streaming test: {e}")

def main():
    """Main test function."""
    
    # Check environment variables
    if not os.getenv("LLM_API_KEY"):
        print("❌ LLM_API_KEY environment variable is required")
        print("Please set your API key:")
        print("export LLM_API_KEY='your-api-key'")
        return
    
    print(f"🔧 Configuration:")
    print(f"  Model: {os.getenv('LLM_MODEL', 'gpt-3.5-turbo')}")
    print(f"  Base URL: {os.getenv('LLM_BASE_URL', 'default')}")
    print(f"  API Key: {'✅ Set' if os.getenv('LLM_API_KEY') else '❌ Not set'}")
    
    # Run tests
    asyncio.run(test_iterative_agent())
    asyncio.run(test_non_streaming())

if __name__ == "__main__":
    main()