# Multi-Agent System Architecture

This directory contains a sophisticated multi-agent system with specialized agents, coordination logic, base classes, and tool integration.

## Structure

```
agents/
├── __init__.py
├── base_agent.py              # Abstract base class for all agents
├── agent_coordinator.py       # Multi-agent coordination and routing
├── langraph_agent.py          # LangGraph workflow implementation
├── iterative_agent.py         # Iterative reasoning agent with controlled loops
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

## Recent Updates

### Improved Iterative Agent User Experience (v2.1)

The iterative agent streaming interface has been enhanced for better user experience:

#### Key Improvements

- **Clean Streaming Interface**: Removed verbose step-by-step progress indicators in favor of natural word-by-word final answer delivery
- **Background Processing**: Complex reasoning and tool execution happen behind the scenes with detailed logging for developers
- **Natural Conversation Flow**: Users experience smooth, ChatGPT-like responses without technical clutter
- **Developer Debugging**: Complete iteration history and tool execution details available in logs and response metadata
- **Error Handling**: User-friendly error messages without exposing technical implementation details
- **Performance Transparency**: Iteration counts and processing metadata available without cluttering the user interface

#### User Experience Benefits

- **Reduced Cognitive Load**: Users focus on the final answer rather than intermediate processing steps
- **Professional Appearance**: Clean, polished interface suitable for production applications
- **Faster Perceived Response**: Word-by-word streaming feels more responsive than chunked updates
- **Consistent Experience**: Matches expectations from modern AI chat interfaces

### Enhanced Tool Registry (v2.0)

The tool registry has been significantly improved to provide better compatibility with LangChain tools and more flexible tool invocation patterns:

#### Key Improvements

- **Enhanced LangChain Support**: Improved handling of LangChain tools with proper `tool_input` parameter formatting
- **Flexible Invocation Patterns**: Support for multiple tool invocation methods:
  - `run(tool_input=param)` for LangChain tools with single parameters
  - `run(tool_input="")` for LangChain tools with empty parameters (improved compatibility)
  - `run(**kwargs)` for LangChain tools with keyword arguments
  - `invoke({"tool_input": param})` for LangChain tools with dictionary parameters
  - `invoke(kwargs)` for advanced LangChain tools
  - Direct function calls for simple tools
- **Automatic Parameter Handling**: Intelligent parameter conversion based on input type
- **Improved Empty Parameter Handling**: Fixed empty parameter case to properly pass `tool_input=""` for better LangChain compatibility
- **Better Error Messages**: Clear error messages for unsupported tool types
- **Backward Compatibility**: Existing tools continue to work without changes

#### Tool Adapter Pattern

The `ToolAdapter` class provides a unified interface for all tool types:

```python
class ToolAdapter:
    def __init__(self, func: Callable):
        self.name = getattr(func, "name", func.__name__)
        self.description = getattr(func, "description", func.__doc__ or "")
        self._func = func
    
    def invoke(self, param: Any = None):
        # Intelligent parameter handling and method selection
        # Supports: run(), invoke(), direct calls
        # Handles: strings, dictionaries, None parameters
```

#### Usage Examples

```python
from src.agents.tools.registry import tool_registry

# Get all tools
tools = tool_registry.get_all_tools()

# Get specific tool
weather_tool = tool_registry.get_tool("get_weather")

# Invoke with different parameter types
result1 = weather_tool.invoke("Mumbai")  # String parameter
result2 = weather_tool.invoke({"location": "Delhi"})  # Dictionary parameter
result3 = weather_tool.invoke()  # No parameters
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
- **Improved Logging**: Benefits from the application's color-coded logging system for easier debugging

### IterativeAgent (`iterative_agent.py`)

Advanced reasoning agent that can solve complex problems through controlled iteration:

- **Controlled Iteration**: Configurable maximum iterations (default: 5) to prevent excessive LLM calls
- **Structured Reasoning**: Follows THOUGHT → ACTION → OBSERVATION → FINAL_ANSWER pattern
- **Tool Integration**: Strategic tool calling during the reasoning process
- **Streaming Support**: Real-time updates with step-by-step progress indicators
- **Response Parsing**: Intelligent parsing of LLM responses using regex patterns
- **Error Handling**: Graceful recovery from tool failures and iteration limits
- **Conversation Context**: Maintains conversation history throughout iterations
- **Final Answer Detection**: Automatically detects when sufficient information is gathered

#### Key Features

- **IterationStep Dataclass**: Tracks each step with thought, action, observation, and completion status
- **Strategic Tool Usage**: Only calls tools when necessary to advance toward the solution
- **Clean Streaming Experience**: Minimal progress indicators with word-by-word final answer delivery
- **Maximum Iteration Safety**: Prevents infinite loops with configurable limits
- **Tool Execution Safety**: Safe tool parameter handling with error recovery
- **Response Format Parsing**: Extracts THOUGHT, ACTION, ACTION_INPUT, and FINAL_ANSWER from LLM responses
- **Background Processing**: Detailed logging for debugging while maintaining clean user interface
- **Enhanced Development Experience**: Color-coded logging with precise source location tracking for debugging complex iterations

#### Usage Patterns

The iterative agent is ideal for complex, multi-step problems:

```python
from src.agents.iterative_agent import IterativeAgent
from src.llm.openai_compatible_llm import OpenAICompatibleLLM

# Initialize agent
llm = OpenAICompatibleLLM(model="gpt-3.5-turbo", api_key="your-key")
agent = IterativeAgent(llm, max_iterations=5)

# Process complex query
final_answer, steps = await agent.process_iteratively(
    "Analyze weather patterns and recommend optimal crops for maximum profit"
)

# Stream processing with clean user experience
async for chunk, is_complete, step_info in agent.stream_process_iteratively(
    "Calculate irrigation costs and create a planting schedule"
):
    if not is_complete:
        print(chunk, end="")  # Clean word-by-word streaming of final answer
```

#### Response Format

The agent expects LLM responses in this format:

```
THOUGHT: [Reasoning about what to do next]
ACTION: [tool_name]
ACTION_INPUT: {"parameter": "value"}

OR for final answers:

THOUGHT: [Final reasoning]
FINAL_ANSWER: [Complete response to user]
```

### AgentCoordinator (`agent_coordinator.py`)

Central coordination system that manages multiple specialized agents with enhanced routing logic:

- **Intelligent Query Routing**: Advanced LLM-based routing that determines optimal processing mode (SIMPLE vs ITERATIVE)
- **Multi-Agent Orchestration**: Coordinates multiple agents for complex queries
- **Iterative Processing Integration**: Routes complex multi-step queries to the iterative agent
- **Weather Query Intelligence**: Smart handling of weather queries based on location specificity
- **Real-time Data Detection**: Automatically routes queries requiring current information to iterative processing
- **Parallel Processing**: Can run multiple agents simultaneously for comprehensive responses
- **Fallback Routing**: Keyword-based fallback when LLM routing fails
- **Response Combination**: Merges responses from multiple agents into coherent answers
- **Streaming Support**: Provides clean streaming responses with minimal visual clutter

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

- **Central Registry**: Manages all available tools with standardized interface
- **Tool Adapter Pattern**: Normalizes different tool types (functions, LangChain tools, custom tools) into consistent interface
- **Enhanced LangChain Compatibility**: Improved support for LangChain tools with proper `tool_input` parameter handling, including fixed empty parameter handling
- **Flexible Invocation**: Supports multiple invocation patterns:
  - Direct function calls for simple tools
  - `run()` method for LangChain tools with proper parameter formatting (including `tool_input=""` for empty parameters)
  - `invoke()` method for advanced LangChain tools with dictionary parameters
- **Dynamic Registration**: Allows runtime tool registration and management
- **Error Handling**: Graceful fallback for unsupported tool types

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
│  │  • Iterative Agent (controlled reasoning loops)                        │ │
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
- **Purpose**: Returns comprehensive location data for Baroda, Jamjodhpur
- **Returns**: Dictionary with city, coordinates, landmarks, demographics, industries
- **LangChain Integration**: Decorated with `@tool` for seamless agent integration
- **Error Handling**: Graceful error handling with fallback responses

#### Weather Tool (`tools/weather_tool.py`)

- **Function**: `get_weather(location: str = "Baroda, Jamjodhpur")`
- **Purpose**: Returns realistic mock weather data for agricultural planning
- **Returns**: Dictionary with temperature, humidity, forecast, UV index, wind conditions
- **LangChain Integration**: Decorated with `@tool` for seamless agent integration
- **Agricultural Focus**: Includes farming-relevant weather metrics
- **HTTP Integration**: Uses requests library for external weather API calls when configured

#### Calculator Tool (`tools/calculator_tool.py`)

- **Function**: `calculate(expression: str)`
- **Purpose**: Safely evaluates mathematical expressions using AST parsing
- **Security**: Uses whitelist of safe operators to prevent code injection
- **Returns**: Dictionary with expression, result, and success status
- **LangChain Integration**: Decorated with `@tool` for seamless LangChain compatibility

### Tool Enhancement Capabilities

With the addition of the `requests` library, tools can now:
- **External API Integration**: Make HTTP calls to real-time data sources
- **Weather API Connectivity**: Connect to live weather services
- **Data Enrichment**: Fetch additional context from external services
- **Real-time Information**: Access current data beyond static responses

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

### Using Iterative Agent

The iterative agent is perfect for complex, multi-step problem solving:

```python
import os
from src.agents.iterative_agent import IterativeAgent
from src.llm.openai_compatible_llm import OpenAICompatibleLLM

# Initialize OpenAI-compatible LLM
llm = OpenAICompatibleLLM(
    model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"), 
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL")
)

# Create iterative agent with custom iteration limit
agent = IterativeAgent(llm, max_iterations=7)

# Process complex query with full iteration history
final_answer, iteration_steps = await agent.process_iteratively(
    "I need to plan my organic farm. What's the weather forecast, "
    "which crops are most profitable, and how much should I invest?"
)

print(f"Final Answer: {final_answer}")
print(f"Completed in {len(iteration_steps)} iterations")

# Stream processing with clean user experience
async for chunk, is_complete, step_info in agent.stream_process_iteratively(
    "Calculate the ROI for switching to organic farming given current weather conditions"
):
    if not is_complete:
        print(chunk, end="")  # Natural word-by-word streaming
    else:
        if step_info and step_info.get("final"):
            print(f"\n✅ Completed in {step_info['total_iterations']} iterations")

# Example of iteration step information
for i, step in enumerate(iteration_steps):
    print(f"Step {step.step_number}: {step.thought}")
    if step.action:
        print(f"  Action: {step.action}({step.action_input})")
    if step.observation:
        print(f"  Result: {step.observation}")
```

### Intelligent LLM Routing Integration

The multi-agent system can integrate with the intelligent LLM routing service for optimal performance:

```python
from src.services.routing_service import routing_service

# Get routing information for a query
query = "How can I optimize my crop yields using data analysis?"
routing_info = routing_service.get_routing_info(query)

print(f"Query complexity: {routing_info['classification']}")
print(f"Confidence: {routing_info['confidence']}")
print(f"Selected model: {routing_info['selected_model']}")

# Get appropriate LLM for the query
llm, model_type = routing_service.get_appropriate_llm(query)
print(f"Using {model_type} model for this query")

# Use with agent coordinator
coordinator = AgentCoordinator(llm)  # Uses the routed LLM
```

#### Routing Benefits for Multi-Agent System

- **Cost Optimization**: Simple agent queries use smaller, faster models
- **Performance**: Complex multi-agent workflows use more capable models
- **Automatic Selection**: No manual model selection required
- **Scalability**: Better resource utilization across different query types

#### Configuration for Routing

```env
# Main LLM for complex multi-agent workflows
LLM_MODEL=gpt-4
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1

# Small LLM for simple agent queries
SMALL_LLM_MODEL=gpt-3.5-turbo
SMALL_LLM_API_KEY=your_api_key
SMALL_LLM_BASE_URL=https://api.openai.com/v1
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

The enhanced tool registry supports multiple tool types and invocation patterns:

#### 1. LangChain Tools (Recommended)

```python
# tools/my_langchain_tool.py
from langchain_core.tools import tool
from typing import Dict, Any

@tool
def my_langchain_tool(param: str) -> Dict[str, Any]:
    """Description of what the tool does.
    
    Args:
        param: Description of the parameter
        
    Returns:
        Dictionary with tool results
    """
    try:
        # Tool implementation
        result = process_param(param)
        return {"result": result, "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}

# Register in tools/registry.py
from .my_langchain_tool import my_langchain_tool

class ToolRegistry:
    def __init__(self):
        self._tools = {
            # ... existing tools
            "my_langchain_tool": ToolAdapter(my_langchain_tool),
        }
```

#### 2. Custom Tool Classes

```python
# tools/my_custom_tool.py
class MyCustomTool:
    def __init__(self):
        self.name = "my_custom_tool"
        self.description = "Custom tool description"
    
    def run(self, tool_input: str) -> dict:
        """LangChain-style run method"""
        return {"result": f"Processed: {tool_input}"}
    
    def invoke(self, params: dict) -> dict:
        """LangChain-style invoke method"""
        return {"result": f"Invoked with: {params}"}

# Register in tools/registry.py
from .my_custom_tool import MyCustomTool

class ToolRegistry:
    def __init__(self):
        self._tools = {
            # ... existing tools
            "my_custom_tool": ToolAdapter(MyCustomTool()),
        }
```

#### 3. Simple Function Tools

```python
# tools/my_simple_tool.py
def my_simple_tool(param: str) -> dict:
    """Simple function tool"""
    return {"result": f"Simple result: {param}"}

# Add metadata for better integration
my_simple_tool.name = "my_simple_tool"
my_simple_tool.description = "Simple function tool description"

# Register in tools/registry.py
from .my_simple_tool import my_simple_tool

class ToolRegistry:
    def __init__(self):
        self._tools = {
            # ... existing tools
            "my_simple_tool": ToolAdapter(my_simple_tool),
        }
```

#### Tool Registry Benefits

- **Automatic Adaptation**: ToolAdapter automatically handles different tool types
- **Consistent Interface**: All tools expose `.name`, `.description`, and `.invoke()` methods
- **Parameter Flexibility**: Supports various parameter formats (strings, dictionaries, None)
- **LangChain Compatibility**: Proper handling of `tool_input` parameter for LangChain tools
- **Error Handling**: Graceful fallback for unsupported tool types

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

# Test iterative agent (create test file)
python -c "
import asyncio
from src.agents.iterative_agent import IterativeAgent
from src.llm.openai_compatible_llm import OpenAICompatibleLLM
import os

async def test_iterative():
    llm = OpenAICompatibleLLM(
        model=os.getenv('LLM_MODEL', 'gpt-3.5-turbo'),
        api_key=os.getenv('LLM_API_KEY'),
        base_url=os.getenv('LLM_BASE_URL')
    )
    agent = IterativeAgent(llm, max_iterations=3)
    
    print('Testing iterative agent...')
    async for chunk, complete, info in agent.stream_process_iteratively('What is 25 * 4 + 10?'):
        print(chunk, end='')
        if complete:
            print(f'\nCompleted in {info.get(\"total_iterations\", 0)} iterations')

asyncio.run(test_iterative())
"
```

### Test Coverage

- **Multi-Agent System**: Agent coordination, routing, and parallel processing
- **Agent Coordinator**: Query routing and response combination
- **Specialized Agents**: Domain-specific functionality and keyword matching
- **Base Agent**: Abstract method implementation and error handling
- **LangGraph Agent**: Tool calling, state management, and streaming
- **Iterative Agent**: Controlled iteration, tool calling, and step tracking
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
