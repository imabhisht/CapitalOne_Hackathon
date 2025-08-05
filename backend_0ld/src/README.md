# Agricultural AI Advisor

An intelligent agricultural advisory system built with LangGraph, Gemini LLM, and specialized tools for farming assistance.

## 🌾 Features

- **Intelligent Query Analysis**: Automatically extracts crop types, issues, and locations from user queries
- **Weather Integration**: Real-time weather data and 3-day forecasts for location-specific advice
- **Agricultural Knowledge Search**: Powered by Exa.AI for up-to-date farming information
- **Specialized Tools**: Irrigation scheduling, pest identification, fertilizer recommendations
- **Conversation Memory**: MongoDB-based chat history for contextual conversations
- **Streaming Responses**: Real-time response generation for better user experience

## 🏗️ Architecture

```
src/
├── config.py          # Configuration and API keys
├── database.py        # MongoDB chat storage
├── llm_client.py      # Gemini LLM integration
├── tools.py           # Agricultural tools (weather, knowledge, etc.)
├── agent.py           # LangGraph agent workflow
├── chat_service.py    # Main chat service interface
├── main.py           # CLI interface for testing
└── __init__.py       # Module exports
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export GEMINI_API_KEY="your_gemini_api_key"
export WEATHER_API_KEY="your_weather_api_key"
export EXA_API_KEY="your_exa_api_key"
export MONGODB_URI="mongodb://localhost:27017"
```

### 3. Run the System

```bash
# Interactive mode
python src/main.py interactive

# Test mode
python src/main.py test

# Example usage
python example_usage.py
```

## 📚 Usage Examples

### Basic Usage

```python
import asyncio
from src.chat_service import generate_complete_response, create_session

async def main():
    session_id = create_session()
    coordinates = {"lat": 40.7128, "lon": -74.0060}
    
    response = await generate_complete_response(
        "When should I irrigate my wheat crop?",
        session_id=session_id,
        coordinates=coordinates
    )
    print(response)

asyncio.run(main())
```

### Streaming Response

```python
import asyncio
from src.chat_service import generate_streaming_response, create_session

async def main():
    session_id = create_session()
    
    async for chunk, is_complete in generate_streaming_response(
        "My tomato plants have yellow leaves",
        session_id=session_id
    ):
        if not is_complete:
            print(chunk, end="", flush=True)
        else:
            print()

asyncio.run(main())
```

## 🔧 Configuration

### API Keys Required

- **GEMINI_API_KEY**: Google Gemini API key for LLM responses
- **WEATHER_API_KEY**: WeatherAPI key for weather data
- **EXA_API_KEY**: Exa.AI key for agricultural knowledge search

### Optional Settings

```python
from src.config import Config

# Customize settings
Config.MAX_TOKENS = 4000
Config.TEMPERATURE = 0.7
Config.STREAMING_DELAY = 0.1
```

## 🛠️ Available Tools

### Weather Tools
- **Current Weather**: Temperature, humidity, conditions
- **3-Day Forecast**: Extended weather predictions
- **Location-based**: Coordinates-based weather data

### Agricultural Knowledge
- **Exa.AI Search**: Real-time agricultural information
- **Domain-specific**: Focused on farming and agriculture
- **Context-aware**: Crop and location-specific results

### Specialized Advice
- **Irrigation Scheduling**: Water management recommendations
- **Pest Identification**: Symptom-based pest control
- **Fertilizer Recommendations**: NPK and application timing
- **Disease Management**: Plant health diagnostics

## 🔄 Agent Workflow

1. **Query Analysis**: Extract crop type, issue, and location
2. **Information Gathering**: Check for missing details
3. **Weather Retrieval**: Get current and forecast data
4. **Knowledge Search**: Find relevant agricultural information
5. **Specialized Advice**: Generate issue-specific recommendations
6. **Response Generation**: Create comprehensive final response

## 📊 Supported Crops

- **Grains**: Wheat, Rice, Corn/Maize
- **Vegetables**: Tomato, Potato, Cabbage, Lettuce, Carrot, Onion
- **Extensible**: Easy to add new crops

## 🐛 Issue Types

- **Irrigation**: Water management and scheduling
- **Pest Control**: Insect and pest identification
- **Disease Management**: Plant health and treatment
- **Fertilization**: Nutrient management
- **Weather**: Climate and environmental factors

## 🗄️ Database Schema

### Chat Messages
```json
{
  "session_id": "uuid",
  "role": "user|assistant",
  "content": "message content",
  "timestamp": "ISO datetime",
  "metadata": {}
}
```

## 🧪 Testing

### Run Tests
```bash
# Test specific queries
python src/main.py test

# Interactive testing
python src/main.py interactive
```

### Example Queries
- "When should I irrigate my wheat crop?"
- "My tomato plants have yellow leaves, what should I do?"
- "What fertilizer should I use for rice?"
- "How do I control pests in my corn field?"
- "What's the weather forecast for my farm?"

## 🔒 Error Handling

The system includes comprehensive error handling:
- **API Failures**: Graceful fallbacks for missing API keys
- **Network Issues**: Retry logic and timeout handling
- **Invalid Input**: Input validation and user feedback
- **Database Errors**: Connection management and recovery

## 🚀 Performance

- **Async Operations**: Non-blocking API calls
- **Caching**: Tool result caching (configurable)
- **Streaming**: Real-time response generation
- **Session Management**: Efficient conversation handling

## 🔧 Customization

### Adding New Tools
```python
# In tools.py
async def new_agricultural_tool(param: str) -> str:
    # Tool implementation
    return "result"

# Register in AGRICULTURAL_TOOLS
AGRICULTURAL_TOOLS["new_tool"] = {
    "function": new_agricultural_tool,
    "description": "Tool description",
    "parameters": {"param": "str"}
}
```

### Extending Agent Logic
```python
# In agent.py
def custom_analysis_node(state: AgentState) -> AgentState:
    # Custom logic
    return state

# Add to workflow
workflow.add_node("custom_analysis", custom_analysis_node)
```

## 📝 License

This project is part of the Capital One Hackathon prototype.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For questions or issues, please refer to the main project documentation or create an issue in the repository. 