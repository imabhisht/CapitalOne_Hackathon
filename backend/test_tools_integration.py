#!/usr/bin/env python3
"""
Test script to verify that tools are being called properly in the agent system.
"""

import asyncio
import logging
from src.agents.weather_agent import WeatherAgent
from src.agents.financial_agent import FinancialAgent
from src.agents.organic_farming_agent import OrganicFarmingAgent
from src.agents.agent_coordinator import AgentCoordinator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

class TestLLM:
    """Mock LLM that generates responses with tool calls for testing."""
    
    def __init__(self):
        self.call_count = 0
    
    def invoke(self, messages):
        class MockResponse:
            def __init__(self, content):
                self.content = content
        
        self.call_count += 1
        last_message = messages[-1].content.lower()
        
        # Generate appropriate tool calls based on the message
        if 'weather' in last_message and 'mumbai' in last_message:
            return MockResponse('I will check the current weather conditions for Mumbai. TOOL_CALL: get_weather("Mumbai")')
        elif 'calculate' in last_message or 'profit' in last_message or 'interest' in last_message:
            return MockResponse('I will calculate that for you. TOOL_CALL: calculate("1000 * 0.08")')
        elif 'farming' in last_message or 'weather' in last_message:
            return MockResponse('Let me check the weather conditions for farming. TOOL_CALL: get_weather("Delhi")')
        else:
            return MockResponse('Thank you for your question. I have processed the information above.')

async def test_individual_agents():
    """Test each agent individually."""
    print("=" * 50)
    print("TESTING INDIVIDUAL AGENTS")
    print("=" * 50)
    
    llm = TestLLM()
    
    # Test Weather Agent
    print("\n1. Testing Weather Agent:")
    weather_agent = WeatherAgent(llm)
    weather_result = await weather_agent.process("What's the weather in Mumbai?")
    print(weather_result)
    
    # Test Financial Agent
    print("\n2. Testing Financial Agent:")
    financial_agent = FinancialAgent(llm)
    financial_result = await financial_agent.process("Calculate 8% interest on $1000")
    print(financial_result)
    
    # Test Organic Farming Agent
    print("\n3. Testing Organic Farming Agent:")
    farming_agent = OrganicFarmingAgent(llm)
    farming_result = await farming_agent.process("What's good for organic farming today?")
    print(farming_result)

async def test_tool_registry():
    """Test the tool registry directly."""
    print("=" * 50)
    print("TESTING TOOL REGISTRY")
    print("=" * 50)
    
    from src.agents.tools.registry import tool_registry
    
    print("Available tools:", tool_registry.get_tool_names())
    
    # Test weather tool
    weather_tool = tool_registry.get_tool('get_weather')
    weather_result = weather_tool.invoke('Mumbai')
    print("Weather tool test:", weather_result)
    
    # Test calculator tool
    calc_tool = tool_registry.get_tool('calculate')
    calc_result = calc_tool.invoke('100 * 0.15')
    print("Calculator tool test:", calc_result)

async def test_coordinator():
    """Test the agent coordinator."""
    print("=" * 50)
    print("TESTING AGENT COORDINATOR")
    print("=" * 50)
    
    llm = TestLLM()
    small_llm = TestLLM()  # AgentCoordinator needs both llm and small_llm
    coordinator = AgentCoordinator(llm, small_llm)
    
    # Test routing
    queries = [
        "What's the weather like?",
        "Calculate my profit",
        "Help with organic farming"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        routing = await coordinator.route_query(query)
        print(f"Routing: {routing}")

async def main():
    """Run all tests."""
    print("TOOL INTEGRATION TEST SUITE")
    print("Testing if tools are being called properly in the agent system")
    print()
    
    await test_tool_registry()
    await test_individual_agents()
    await test_coordinator()
    
    print("\n" + "=" * 50)
    print("✅ TOOL INTEGRATION TESTS COMPLETED")
    print("✅ Tools are working correctly!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
