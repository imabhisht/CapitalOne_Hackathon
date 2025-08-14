# Multi-Agent System

This directory contains a sophisticated multi-agent system with specialized agents and intelligent routing.

## Architecture Overview

```
Multi-Agent System
├── Agent Coordinator (Routes queries to appropriate agents)
├── Specialized Agents
│   ├── Organic Farming Agent (Agricultural advice)
│   ├── Financial Agent (Financial calculations & advice)
│   ├── Weather Agent (Weather info & agricultural planning)
│   └── General Chat Agent (General conversations)
└── Base Agent (Common functionality)
```

## Components

### 1. Agent Coordinator (`agent_coordinator.py`)

The central orchestrator that:
- Analyzes incoming queries using LLM-based routing
- Determines which agent(s) should handle each query
- Supports both sequential and parallel agent execution
- Combines responses from multiple agents when needed

**Key Features:**
- Intelligent query routing using OpenAI-compatible LLM
- Parallel processing for complex queries requiring multiple expertise areas
- Fallback routing based on keyword matching
- Response combination and formatting

### 2. Specialized Agents

#### Organic Farming Agent (`organic_farming_agent.py`)
- **Expertise**: Organic farming practices, sustainable agriculture, crop management
- **Keywords**: organic, farming, agriculture, crop, soil, compost, pest, sustainable
- **Use Cases**: Crop advice, pest management, soil health, organic certification

#### Financial Agent (`financial_agent.py`)
- **Expertise**: Financial planning, calculations, investment advice, agricultural economics
- **Keywords**: finance, money, budget, investment, loan, calculate, profit, ROI
- **Tools**: Calculator tool for mathematical computations
- **Use Cases**: Farm profitability, investment analysis, loan calculations

#### Weather Agent (`weather_agent.py`)
- **Expertise**: Weather information, agricultural weather planning, seasonal advice
- **Keywords**: weather, temperature, rain, forecast, climate, irrigation
- **Tools**: Weather tool, location tool
- **Use Cases**: Weather forecasts, irrigation planning, planting schedules

#### General Chat Agent (`general_chat_agent.py`)
- **Expertise**: General conversations, explanations, non-specialized queries
- **Keywords**: hello, help, explain, general conversation terms
- **Use Cases**: Greetings, general questions, fallback for unspecialized queries

### 3. Base Agent (`base_agent.py`)

Abstract base class providing:
- Common LLM interaction patterns
- Streaming response capabilities
- Error handling
- Message processing framework

## Usage

### Basic Usage

```python
from src.services.multi_agent_service import multi_agent_service
from src.models.chat_request import ChatRequest

# Create a request
request = ChatRequest(message="How can I improve my organic tomato yield?")

# Get streaming response
async for chunk, is_complete in multi_agent_service.generate_streaming_response(request):
    if not is_complete:
        print(chunk, end='')
    else:
        print()  # New line when complete
```

### Configuration

Set environment variables:
```bash
export LLM_API_KEY="your-api-key"
export LLM_MODEL="gpt-3.5-turbo"  # or gemini-2.5-flash, claude-3-sonnet, etc.
export LLM_BASE_URL="https://api.openai.com/v1"  # or provider-specific endpoint
export USE_MULTI_AGENT="true"  # Enable multi-agent mode
```

### Query Examples

#### Single Agent Queries
- **Organic Farming**: "What's the best organic fertilizer for tomatoes?"
- **Financial**: "Calculate the ROI on a $10,000 farm investment"
- **Weather**: "What's the weather forecast for farming this week?"
- **General**: "Hello, how can you help me?"

#### Multi-Agent Queries (Parallel Processing)
- "What's the profit potential of organic farming given current weather conditions?"
- "How much should I invest in irrigation systems for organic vegetables?"
- "Best organic crops for this climate and their financial returns?"

## Agent Routing Logic

The coordinator uses a two-stage routing process:

### 1. LLM-Based Routing
Uses OpenAI-compatible LLM to analyze queries and determine:
- Which agents should handle the query
- Whether parallel processing is beneficial
- Priority order for sequential processing

### 2. Fallback Keyword Matching
If LLM routing fails, uses keyword matching:
- Checks each agent's keyword list
- Selects agents with matching keywords
- Defaults to general agent if no matches

## Response Combination

For multi-agent responses:

### Parallel Processing
```
Here's what I found from multiple perspectives:

**Organic Farming Perspective:**
[Farming advice response]

**Financial Perspective:**
[Financial analysis response]
```

### Sequential Processing
Agents process in order, with each building on previous responses.

## Testing

Run the test script:
```bash
cd backend
python test_multi_agent.py
```

This tests:
- Agent availability
- Query routing
- Response generation
- Parallel processing
- Error handling

## API Endpoints

### Get Agent Information
```http
GET /agents/info
```

Returns information about all available agents and their capabilities.

### Health Check
```http
GET /health
```

Includes multi-agent service status in the health check response.

### OpenAI API Compatibility

The multi-agent system is accessible through OpenAI-compatible endpoints:

```http
POST /v1/chat/completions
```

This allows third-party tools (like Open WebUI) to interact with the multi-agent system using standard OpenAI API format, automatically routing queries to appropriate specialized agents.

## Configuration

### Environment Variables
- `USE_MULTI_AGENT`: Enable/disable multi-agent mode (default: true)
- `LLM_API_KEY`: Required for LLM functionality
- `LLM_MODEL`: LLM model to use (default: gpt-3.5-turbo)
- `LLM_BASE_URL`: API endpoint for LLM provider (default: OpenAI)

### Agent Configuration
Edit `src/config/multi_agent_config.py` to:
- Enable/disable specific agents
- Configure parallel processing
- Set response parameters
- Adjust LLM settings

## Adding New Agents

1. **Create Agent Class**
```python
from .base_agent import BaseAgent

class MyNewAgent(BaseAgent):
    def __init__(self, llm):
        system_prompt = "Your specialized prompt here..."
        super().__init__("My New Agent", llm, system_prompt)
    
    def can_handle(self, query: str) -> bool:
        # Logic to determine if this agent can handle the query
        return "my_keyword" in query.lower()
    
    def get_keywords(self) -> List[str]:
        return ["my_keyword", "another_keyword"]
```

2. **Register in Coordinator**
```python
# In agent_coordinator.py
from .my_new_agent import MyNewAgent

class AgentCoordinator:
    def __init__(self, llm: OpenAICompatibleLLM):
        self.agents = {
            # ... existing agents
            "my_new": MyNewAgent(llm)
        }
```

3. **Update Configuration**
```python
# In multi_agent_config.py
AGENTS_ENABLED = {
    # ... existing agents
    "my_new": True
}
```

## Best Practices

1. **Agent Specialization**: Keep agents focused on specific domains
2. **Keyword Selection**: Choose distinctive keywords that don't overlap
3. **System Prompts**: Write clear, specific prompts for each agent
4. **Error Handling**: Always handle exceptions gracefully
5. **Testing**: Test each agent individually and in combination
6. **Performance**: Monitor response times for parallel processing

## Troubleshooting

### Common Issues

1. **Agent Not Available**: Check LLM_API_KEY configuration
2. **Poor Routing**: Review agent keywords and system prompts
3. **Slow Responses**: Consider reducing parallel agents or conversation history
4. **Tool Errors**: Verify tool implementations and parameter passing

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This provides detailed information about:
- Query routing decisions
- Agent selection process
- Tool execution
- Response generation