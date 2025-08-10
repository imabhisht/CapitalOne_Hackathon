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

# Initialize
llm = GeminiLLM(model="gemini-2.0-flash-exp", api_key=api_key)
agent = LangGraphAgent(llm)

# Use streaming
async for chunk, is_complete in agent.stream_invoke("What's the weather in Baroda?"):
    if not is_complete:
        print(chunk, end='')
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

## Testing

Run the test script to verify agent functionality:

```bash
cd backend
python test_agent.py
```

This will test various queries including location, weather, calculations, and general conversation.
