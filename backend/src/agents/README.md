# LangGraph Agent Structure

This directory contains the LangGraph agent implementation with a modular tool system.

## Structure

```
agents/
├── __init__.py
├── langraph_agent.py      # Main LangGraph agent implementation
├── tools/                 # Tool directory
│   ├── __init__.py
│   ├── registry.py        # Tool registry for managing all tools
│   ├── location_tool.py   # Location information tool
│   ├── weather_tool.py    # Weather information tool
│   └── calculator_tool.py # Mathematical calculation tool
└── README.md             # This file
```

## Components

### LangGraphAgent (`langraph_agent.py`)

- Main agent class that orchestrates tool calls using proper LangGraph patterns
- Uses StateGraph with proper state management and message handling
- Implements conditional edges for tool calling workflow
- Supports streaming responses and conversation history
- Handles tool execution with error recovery and state tracking
- **Tool Call Detection**: Uses regex patterns to extract `TOOL_CALL:` instructions from LLM responses
- **State Management**: Tracks tool execution state to prevent infinite loops
- **Gemini Integration**: Works with Gemini LLM via OpenAI SDK compatibility
- **Enhanced Debugging**: Tool descriptions are logged during initialization for better development visibility

### Tool Registry (`tools/registry.py`)

- Central registry for all available tools
- Provides methods to get tools by name or get all tools
- Allows dynamic tool registration

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

### In Chat Service

The agent is integrated into the chat service and automatically handles tool calls based on user queries.

```python
from src.agents.langraph_agent import LangGraphAgent
from src.llm.gemini_llm import GeminiLLM

# Initialize Gemini LLM (uses OpenAI SDK format)
llm = GeminiLLM(model="gemini-2.5-flash", api_key=api_key)
agent = LangGraphAgent(llm)

# Use streaming
async for chunk, is_complete in agent.stream_invoke("What's the weather in Baroda?"):
    if not is_complete:
        print(chunk, end='')
```

### Tool Call Format

The agent uses a specific format for tool calls:
- `TOOL_CALL: tool_name()` - for tools without parameters
- `TOOL_CALL: tool_name("parameter")` - for tools with parameters

Examples:
- `TOOL_CALL: get_location()` - Get location information
- `TOOL_CALL: get_weather("Baroda, Jamjodhpur")` - Get weather for location
- `TOOL_CALL: calculate("25 * 4 + 10")` - Perform calculation

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

### Tool Debugging

The agent includes enhanced debugging capabilities:
- Tool descriptions are automatically logged during initialization
- This helps developers verify which tools are loaded and available
- Useful for troubleshooting tool registration issues

### Debug Output Example

When the agent initializes, you'll see output like:
```
- get_location: Returns location information for Baroda, Jamjodhpur
- get_weather: Get weather information for a specific location
- calculate: Safely evaluate mathematical expressions
```

## Testing

Run the test script to verify agent functionality:

```bash
cd backend
python test_agent.py
```

This will test various queries including location, weather, calculations, and general conversation.
