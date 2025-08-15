# Iterative Agent System

## Overview

The Iterative Agent System implements a looping mechanism that allows agents to complete complex tasks by:

1. **Iterative Tool Calling**: Agents can call multiple tools in sequence
2. **LLM Reasoning**: Between each tool call, the LLM reasons about the results and decides next steps
3. **Controlled Loop Count**: Maximum of 5 iterations to prevent excessive LLM calls
4. **Comprehensive Response**: Final answer based on all previous question-answer pairs

## Architecture

### Core Components

1. **IterativeAgent** (`src/agents/iterative_agent.py`)
   - Main iterative processing logic
   - Manages iteration steps and tool execution
   - Controls loop count (default: 5 iterations)

2. **Enhanced AgentCoordinator** (`src/agents/agent_coordinator.py`)
   - Routes queries between simple and iterative processing
   - Determines when to use iterative vs. simple agents
   - Integrates with existing multi-agent system

3. **IterationStep** (dataclass)
   - Represents each step in the reasoning process
   - Tracks thoughts, actions, observations, and completion status

### Processing Flow

```
User Query → Routing Decision → Processing Mode

Simple Mode:
Query → Specialized Agent → Response

Iterative Mode:
Query → Iteration 1 (Thought → Action → Observation)
      → Iteration 2 (Thought → Action → Observation)
      → ...
      → Final Answer (max 5 iterations)
```

## Features

### 1. Smart Routing

The system automatically determines whether to use simple or iterative processing based on query complexity:

**Iterative Mode Triggers:**
- Queries requiring multiple steps
- Tasks needing data gathering and analysis
- Complex problem-solving scenarios
- Calculations with external data
- Multi-source information combination
- Weather queries without specific location (need to get location first)
- Queries requiring real-time data or current information

**Simple Mode Triggers:**
- Direct questions with straightforward answers
- General conversations
- Single-domain expertise queries
- Weather queries with specific location already provided

### 2. Controlled Iteration

- **Maximum Iterations**: 5 (configurable)
- **Early Termination**: Stops when final answer is reached
- **Fallback**: Provides best available answer if max iterations reached
- **Error Handling**: Graceful handling of tool failures

### 3. Streaming Support

Clean streaming experience with focus on results:
- Minimal progress indicators during processing
- Background iteration processing with detailed logging
- Word-by-word streaming of final answers
- Natural conversation flow without visual clutter

### 4. Tool Integration

Seamlessly integrates with existing tool registry:
- Weather tools
- Calculation tools
- Location services
- Data analysis tools

## Usage Examples

### Simple Query (Uses Simple Mode)
```
Query: "What's the weather in Mumbai?"
Mode: SIMPLE
Agent: weather
Response: Direct weather information for Mumbai
```

### Weather Query Without Location (Uses Iterative Mode)
```
Query: "What's the weather today?"
Mode: ITERATIVE

Iteration 1:
- Thought: User didn't specify location, need to get their location first
- Action: get_location
- Observation: Location detected as Baroda, Jamjodhpur

Iteration 2:
- Thought: Now I can get weather for the detected location
- Action: get_weather
- Final Answer: Current weather for Baroda with farming recommendations
```

### Complex Query (Uses Iterative Mode)
```
Query: "Calculate the ROI for a 10-acre organic farm with current market prices"

Iteration 1:
- Thought: Need to gather current market prices for organic crops
- Action: get_market_data
- Observation: Current organic crop prices retrieved

Iteration 2:
- Thought: Need to calculate costs for 10-acre farm operation
- Action: calculate
- Observation: Operating costs calculated

Iteration 3:
- Thought: Now I can calculate ROI with revenue and costs
- Action: calculate
- Final Answer: Complete ROI analysis with breakdown
```

## API Endpoints

### 1. Test Iterative Agent
```http
POST /agents/iterative/test
Content-Type: application/json

{
  "message": "Your query here"
}
```

Returns routing decision and system information.

### 2. Stream Iterative Response
```http
POST /agents/iterative/stream
Content-Type: application/json

{
  "message": "Your complex query here"
}
```

Returns Server-Sent Events stream with iterative processing updates.

### 3. Regular Chat (Auto-routing)
```http
POST /chat/stream
Content-Type: application/json

{
  "message": "Your query here",
  "session_id": "optional-session-id"
}
```

Automatically routes to simple or iterative processing.

## Testing

### 1. Test Script
```bash
cd backend
python test_iterative_agent.py
```

### 2. Web Interface
Navigate to: `http://localhost:5050/static/iterative_test.html`

Features:
- Quick test buttons for common scenarios
- Custom query input
- Routing analysis
- Real-time streaming display
- System status checking

### 3. Test Queries

**Simple Queries:**
- "What's the weather in Mumbai?"
- "Hello, how are you?"
- "What is 25 * 4?"

**Complex Queries (Automatically use Iterative Mode):**
- "What's the weather today?" (no location specified)
- "Calculate the ROI for a 10-acre organic farm"
- "Plan a complete farming strategy including weather and costs"
- "Research and compare corn vs soybean profitability"
- "Find weather and determine if good for planting tomatoes"
- "Is it good weather for planting?" (needs location + weather + analysis)

## Configuration

### Environment Variables
```bash
# Required
LLM_API_KEY=your_api_key
LLM_MODEL=your_model_name
LLM_BASE_URL=your_llm_endpoint

# Optional
SMALL_LLM_API_KEY=your_small_model_api_key
SMALL_LLM_MODEL=your_small_model_name
SMALL_LLM_BASE_URL=your_small_model_endpoint

# System Settings
USE_MULTI_AGENT=true
USE_SMART_ROUTING=true
```

### Iteration Limits
```python
# Default: 5 iterations
iterative_agent = IterativeAgent(llm, max_iterations=5)

# Custom limit
iterative_agent = IterativeAgent(llm, max_iterations=3)
```

## Benefits

1. **Efficiency**: Prevents excessive LLM calls with controlled iteration count
2. **Clean Experience**: Minimal visual clutter with focus on final answers
3. **Natural Interaction**: Word-by-word streaming feels like human conversation
4. **Flexibility**: Handles both simple and complex queries appropriately
5. **Reliability**: Graceful error handling and fallback mechanisms
6. **Scalability**: Easy to add new tools and extend functionality
7. **Developer Friendly**: Detailed logging for debugging while maintaining clean user experience
8. **Performance Transparency**: Iteration metadata available without cluttering user interface

## Integration

The iterative agent system integrates seamlessly with:
- Existing chat service
- Multi-agent coordinator
- Tool registry
- MongoDB conversation storage
- Streaming response system

## Future Enhancements

1. **Dynamic Iteration Limits**: Adjust based on query complexity
2. **Parallel Tool Execution**: Execute multiple tools simultaneously
3. **Learning from History**: Improve routing based on past interactions
4. **Custom Agent Workflows**: Define specific iteration patterns for different domains
5. **Performance Metrics**: Track iteration efficiency and success rates

## Troubleshooting

### Common Issues

1. **No Response**: Check LLM API key and endpoint configuration
2. **Routing Errors**: Verify small LLM configuration for routing decisions
3. **Tool Failures**: Check tool registry and individual tool configurations
4. **Streaming Issues**: Ensure proper CORS and connection settings

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Check
```http
GET /health
```

Returns system status including iterative agent availability.