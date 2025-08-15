#!/usr/bin/env python3
"""
Test script to verify the clean iterative agent response.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.iterative_agent import IterativeAgent
from src.llm.openai_compatible_llm import OpenAICompatibleLLM

# Load environment variables
load_dotenv()

async def test_clean_response():
    """Test the iterative agent with clean streaming response."""
    try:
        # Initialize LLM (using environment variables)
        llm = OpenAICompatibleLLM(
            model=os.getenv('LLM_MODEL', 'gpt-3.5-turbo'),
            api_key=os.getenv('LLM_API_KEY'),
            base_url=os.getenv('LLM_BASE_URL')
        )
        
        # Initialize iterative agent
        agent = IterativeAgent(llm, max_iterations=3)
        
        # Test with a simple location query
        print('Testing iterative agent with clean streaming...')
        print('Query: what is my location?')
        print('Response:')
        print('-' * 50)
        
        async for chunk, is_complete, step_info in agent.stream_process_iteratively('what is my location?'):
            if chunk:
                print(chunk, end='', flush=True)
            if is_complete:
                print('\n' + '-' * 50)
                print('[STREAMING COMPLETE]')
                if step_info:
                    print(f"Total iterations: {step_info.get('total_iterations', 'N/A')}")
                break
                
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_clean_response())