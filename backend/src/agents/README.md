# Multi-Agent System Architecture

This directory contains a sophisticated multi-agent system with specialized agents, coordination logic, base classes, and tool integration.

## Structure

```
agents/
├── __init__.py
├── base_agent.py              # Abstract base class for all agents
├── agent_coordinator.py       # Multi-agent coordination and routing
├── langraph_agent.py          # LangGraph workflow implementation
├── intent_gathering_agent.py  # Intent clarification agent
├── organic_farming_agent.py   # Organic farming specialist agent
├── financial_agent.py         # Financial advice specialist agent
├── weather_agent.py           # Weather information specialist agent
├── general_chat_agent.py      # General conversation handler agent
├── tools/                     # Tool directory
│   ├── __init__.py
│   ├── registry.py            # Tool registry for managing all tools
│   ├── location_tool.py       # Location information tool
│   ├── weather_tool.py        # Weather information tool
│   └── calculator_tool.py     # Mathematical calculation tool
└── README.md                 # This file
```

## Components

### BaseAgent (`base_agent.py`)

Abstract base class providing common functionality for all specialized agents:

- **Abstract Interface**: Defines standard methods (`can_handle`, `get_keywords`, `process`)
- **LLM Integration**: Built-in OpenAI-compatible LLM support with conversation history management
- **Streaming Support**: `stream_process` method for word-by-word response streaming
- **Error Handling**: Graceful error recovery with user-friendly error messages
- **Conversation Management**: Automatic handling of conversation history (last 5 messages)
- **System Prompt**: Configurable system prompts for specialized agent behavior

### LangGraphAgent (`langraph_agent.py`)

Main workflow orchestrator that implements LangGraph patterns:

- **StateGraph Workflow**: Proper LangGraph implementation with state management
- **Tool Call Detection**: Uses regex patterns to extract `TOOL_CALL:` instructions from LLM responses
- **State Management**: Tracks tool execution state to prevent infinite loops
- **Conditional Routing**: Smart routing between model calls and tool execution
- **LLM Integration**: Works with any OpenAI SDK-compatible LLM provider
- **Enhanced Debugging**: Tool descriptions are logged during initialization for better development visibility

### AgentCoordinator (`agent_coordinator.py`)

Central coordination system that manages multiple specialized agents:

- **Query Routing**: Intelligent routing of queries to appropriate agents using LLM-based analysis
- **Multi-Agent Orchestration**: Coordinates multiple agents for complex queries
- **Parallel Processing**: Can run multiple agents simultaneously for comprehensive responses
- **Fallback Routing**: Keyword-based fallback when LLM routing fails
- **Response Combination**: Merges responses from multiple agents into coherent answers
- **Streaming Support**: Provides streaming responses for real-time interaction

### Specialized Agents

#### OrganicFarmingAgent (`organic_farming_agent.py`)
- **Expertise**: Organic farming practices, sustainable agriculture, soil health, pest management
- **Keywords**: organic, farming, agriculture, crop, soil, compost, fertilizer, pest, sustainable
- **Capabilities**: Provides practical organic farming advice and guidance

#### FinancialAgent (`financial_agent.py`)
- **Expertise**: Financial planning, investment advice, loan calculations, agricultural economics
- **Keywords**: finance, money, budget, investment, loan, profit, ROI, calculate
- **Tool Integration**: Uses calculator tool for financial computations
- **Capabilities**: Financial analysis with mathematical calculations

#### WeatherAgent (`weather_agent.py`)
- **Expertise**: Weather information, agricultural weather planning, seasonal patterns
- **Keywords**: weather, temperature, rain, forecast, climate, irrigation
- **Tool Integration**: Uses weather and location tools for current conditions
- **Capabilities**: Weather-based agricultural advice and planning

#### GeneralChatAgent (`general_chat_agent.py`)
- **Expertise**: General conversations, explanations, creative writing, problem-solving
- **Keywords**: hello, help, what, how, explain, general conversation terms
- **Capabilities**: Handles queries not covered by specialized agents (fallback agent)

### IntentGatheringAgent (`intent_gathering_agent.py`)

Specialized agent for clarifying user intent through conversational interaction:

- **Intent Clarification**: Asks specific questions to understand complete user intent
- **Parameter Gathering**: Collects all necessary parameters for task execution
- **Conversational Flow**: Natural dialogue to gather missing information
- **Intent Completion**: Signals when sufficient information is collected with `INTENT_COMPLETE:`
- **Low Temperature**: Uses temperature 0.3 for more focused, consistent responses

### Tool Registry (`tools/registry.py`)

- Central registry for all available tools
- Provides methods to get tools by name or get all tools
- Allows dynamic tool registration

## Agent Architecture Overview

The multi-agent system follows a hierarchical architecture with intelligent routing:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Multi-Agent Service                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        Agent Coordinator                               │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐ │ │
│  │  │ Query Routing   │  │ Parallel Proc.  │  │ Response Combination    │ │ │
│  │  │ (LLM-based)     │  │ Coordination    │  │ & Streaming             │ │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Specialized Agents                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │ Organic     │ │ Financial   │ │ Weather     │ │ General Chat            │ │
│  │ Farming     │ │ Agent       │ │ Agent       │ │ Agent                   │ │
│  │ Agent       │ │             │ │             │ │ (Fallback)              │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Base Agent Class                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  • Abstract interface (can_handle, get_keywords)                       │ │
│  │  • LLM integration with conversation history                           │ │
│  │  • Streaming support with word-by-word output                          │ │
│  │  • Error handling and graceful recovery                                │ │
│  │  • Tool integration capabilities                                       │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Supporting Components                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │  • LangGraph Agent (StateGraph workflow)                               │ │
│  │  • Intent Gathering Agent (conversational clarification)               │ │
│  │  • Tool Registry (location, weather, calculator tools)                 │ │
│  │  • Configuration Management (MultiAgentConfig)                         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **Separation of Concerns**: Each agent has a specific domain responsibility
2. **Intelligent Routing**: LLM-based query analysis determines optimal agent selection
3. **Inheritance**: Common functionality is provided by the `BaseAgent` base class
4. **Modularity**: Tools and agents can be added independently
5. **Extensibility**: New specialized agents can easily inherit from `BaseAgent`
6. **Parallel Processing**: Multiple agents can work simultaneously on complex queries
7. **Configuration Management**: Centralized configuration via `MultiAgentConfig`
8. **State Management**: Proper state tracking throughout the workflow
9. **Graceful Fallback**: Keyword-based routing when LLM routing fails

### Available Tools

#### Location Tool (`tools/location_tool.py`)

- **Function**: `get_location(query: str = "")`
- **Purpose**: Returns static location data for Baroda, Jamjodhpur
- **Returns**: Dictionary with city, coordinates, landmarks, etc.

#### Weather Tool (`tools/weather_tool.py`)

- **Function**: `get_weather(location: str = "Baroda, Jamjodhpur")`
- **Purpose**: Returns mock weather data for a location
- **Returns**: Dictionary with temperature, humidity, forecast, etc.

#### Calculator Tool (`tools/calculator_tool.py`)

- **Function**: `calculate(expression: str)`
- **Purpose**: Safely evaluates mathematical expressions
- **Returns**: Dictionary with expression, result, and success status

## Usage

### Using the Multi-Agent System

The recommended way to use the agent system is through the `MultiAgentService`:

```python
from src.services.multi_agent_service import multi_agent_service
from src.models.chat_request import ChatRequest

# Check if service is available
if multi_agent_service.is_available():
    # Create a chat request
    request = ChatRequest(
        message="How can I improve my organic tomato yield and what's the expected profit?",
        conversation_history=[
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi! How can I help you today?"}
        ]
    )
    
    # Get streaming response
    async for chunk, is_complete in multi_agent_service.generate_streaming_response(request):
        if not is_complete:
            print(chunk, end="")
    
    # Get agent information
    agent_info = multi_agent_service.get_agent_info()
    print(f"Available agents: {list(agent_info.keys())}")
```

### Using the Agent Coordinator Directly

For more control over agent routing:

```python
import os
from src.agents.agent_coordinator import AgentCoordinator
from src.llm.openai_compatible_llm import OpenAICompatibleLLM

# Initialize coordinator
llm = OpenAICompatibleLLM(
    model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"), 
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL")
)
coordinator = AgentCoordinator(llm)

# Route a query
routing = await coordinator.route_query("What's the weather for farming?")
print(f"Selected agents: {routing['agents']}")
print(f"Parallel processing: {routing['parallel']}")

# Process with routing
response = await coordinator.process_query("What's the weather for farming?")
print(response)

# Stream response
async for chunk, is_complete in coordinator.stream_process_query("Weather forecast?"):
    if not is_complete:
        print(chunk, end='')
```

### Creating Specialized Agents

Inherit from `BaseAgent` to create new specialized agents:

```python
from src.agents.base_agent import BaseAgent
from src.llm.openai_compatible_llm import OpenAICompatibleLLM

class CustomAgent(BaseAgent):
    def __init__(self, llm: OpenAICompatibleLLM):
        super().__init__(
            name="CustomAgent",
            llm=llm,
            system_prompt="You are a specialist in [your domain]. Provide expert advice."
        )
    
    def can_handle(self, query: str) -> bool:
        keywords = self.get_keywords()
        return any(keyword in query.lower() for keyword in keywords)
    
    def get_keywords(self) -> List[str]:
        return ["custom", "specialist", "domain-specific", "keywords"]

# Register with coordinator (modify agent_coordinator.py)
# Add to the agents dictionary in AgentCoordinator.__init__
```

### Using LangGraph Agent

The LangGraph agent handles complex workflows with tool calling:

```python
import os
from src.agents.langraph_agent import LangGraphAgent
from src.llm.openai_compatible_llm import OpenAICompatibleLLM

# Initialize OpenAI-compatible LLM
llm = OpenAICompatibleLLM(
    model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"), 
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL")
)
agent = LangGraphAgent(llm)

# Use streaming
async for chunk, is_complete in agent.stream_invoke("What's the weather in Baroda?"):
    if not is_complete:
        print(chunk, end='')
```

### Configuration Management

Configure the multi-agent system:

```python
import os
from src.config import MultiAgentConfig

# Check current configuration
config = MultiAgentConfig.get_config()
print(f"Agents enabled: {config['agents_enabled']}")
print(f"Parallel processing: {config['enable_parallel_processing']}")

# Check if specific agent is enabled
if MultiAgentConfig.is_agent_enabled("organic_farming"):
    print("Organic farming agent is enabled")

# Validate configuration
issues = MultiAgentConfig.validate_config()
if issues:
    print(f"Configuration issues: {issues}")

# Environment variables
# USE_MULTI_AGENT=true
# LLM_MODEL=gpt-3.5-turbo  # or gemini-2.5-flash, claude-3-sonnet, etc.
# LLM_API_KEY=your_api_key
# LLM_BASE_URL=https://api.openai.com/v1  # or provider-specific endpoint
```

**Configuration Updates**: The system now supports flexible multi-provider LLM configuration:
- Use `LLM_MODEL` to specify the model (e.g., `gemini-2.5-flash`, `gpt-4`, `claude-3-sonnet`)
- Use `LLM_API_KEY` for the API key
- Use `LLM_BASE_URL` to specify the provider endpoint
- This allows easy switching between different LLM providers without code changes

**Provider Examples**:
- **Gemini**: `LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/`
- **OpenAI**: `LLM_BASE_URL=https://api.openai.com/v1` (or omit for default)
- **Local Models**: `LLM_BASE_URL=http://localhost:11434/v1`

### Tool Call Format

The agent uses a specific format for tool calls:
- `TOOL_CALL: tool_name()` - for tools without parameters
- `TOOL_CALL: tool_name("parameter")` - for tools with parameters

Examples:
- `TOOL_CALL: get_location()` - Get location information
- `TOOL_CALL: get_weather("Baroda, Jamjodhpur")` - Get weather for location
- `TOOL_CALL: calculate("25 * 4 + 10")` - Perform calculation

### Adding New Specialized Agents

1. Create a new agent file inheriting from `BaseAgent`
2. Implement the required abstract methods
3. Define specialized behavior and keywords
4. Register the agent in `AgentCoordinator`
5. Update `MultiAgentConfig` if needed

Example:

```python
# agents/calculation_agent.py
from typing import List
from src.agents.base_agent import BaseAgent
from src.llm.openai_compatible_llm import OpenAICompatibleLLM

class CalculationAgent(BaseAgent):
    def __init__(self, llm: OpenAICompatibleLLM):
        super().__init__(
            name="CalculationAgent",
            llm=llm,
            system_prompt="You are a mathematics expert. Help with calculations and math problems."
        )
    
    def can_handle(self, query: str) -> bool:
        math_keywords = ["calculate", "math", "equation", "solve", "+", "-", "*", "/"]
        return any(keyword in query.lower() for keyword in math_keywords)
    
    def get_keywords(self) -> List[str]:
        return ["calculate", "math", "equation", "solve", "arithmetic", "algebra"]

# Register in agent_coordinator.py
from .calculation_agent import CalculationAgent

class AgentCoordinator:
    def __init__(self, llm: OpenAICompatibleLLM):
        self.agents = {
            # ... existing agents
            "calculation": CalculationAgent(llm),
        }

# Update multi_agent_config.py
AGENTS_ENABLED = {
    # ... existing agents
    "calculation": True,
}
```

### Adding New Tools

1. Create a new tool file in `tools/` directory
2. Define your tool using the `@tool` decorator from `langchain_core.tools`
3. Register it in `tools/registry.py`

Example:

```python
# tools/my_new_tool.py
from langchain_core.tools import tool

@tool
def my_new_tool(param: str) -> dict:
    """Description of what the tool does."""
    return {"result": "some result"}

# In tools/registry.py
from .my_new_tool import my_new_tool

class ToolRegistry:
    def __init__(self):
        self._tools = {
            # ... existing tools
            "my_new_tool": my_new_tool,
        }
```

## Debugging & Development

### Agent Development

The base agent architecture provides several debugging features:

- **Error Logging**: All agents log errors with agent name for easy identification
- **Conversation History**: Automatic management of conversation context
- **Streaming Debug**: Word-by-word streaming with configurable delays
- **Abstract Method Enforcement**: Ensures all specialized agents implement required methods

### Tool Debugging

The LangGraph agent includes enhanced debugging capabilities:
- Tool descriptions are automatically logged during initialization
- This helps developers verify which tools are loaded and available
- Useful for troubleshooting tool registration issues

### Debug Output Example

When the LangGraph agent initializes, you'll see output like:
```
- get_location: Returns location information for Baroda, Jamjodhpur
- get_weather: Get weather information for a specific location
- calculate: Safely evaluate mathematical expressions
```

### Intent Gathering Debug

The intent gathering agent provides debug information:
- Shows when intent is incomplete and what information is needed
- Logs when intent is marked as complete with `INTENT_COMPLETE:`
- Tracks conversation flow for intent clarification

## Testing

Run the test scripts to verify agent functionality:

```bash
cd backend
python test_multi_agent.py  # Test multi-agent system and routing
python test_agent.py        # Test LangGraph agent functionality
python test_langraph.py     # Test LangGraph workflows
python simple_test.py       # Basic system tests
```

### Test Coverage

- **Multi-Agent System**: Agent coordination, routing, and parallel processing
- **Agent Coordinator**: Query routing and response combination
- **Specialized Agents**: Domain-specific functionality and keyword matching
- **Base Agent**: Abstract method implementation and error handling
- **LangGraph Agent**: Tool calling, state management, and streaming
- **Intent Gathering**: Intent clarification and completion detection
- **Configuration**: Multi-agent configuration validation
- **Tool Integration**: Location, weather, and calculation tools

### Example Test Output

```bash
python test_multi_agent.py

🤖 Testing Multi-Agent System
==================================================
✅ Multi-agent service is available

📋 Available Agents:
  • Organic Farming Guide: Specialized in organic_farming
  • Financial Advisor: Specialized in financial
  • Weather Expert: Specialized in weather
  • General Assistant: Specialized in general

🧪 Running 5 test queries...
==================================================

1. Query: What's the weather like for farming today?
   Expected: weather
   Response: Based on current weather conditions in Baroda, Jamjodhpur...
   ✅ Response received

2. Query: How can I improve my organic tomato yield?
   Expected: organic_farming
   Response: Here are several organic methods to improve your tomato yield...
   ✅ Response received
```
