# Agricultural AI Advisor Backend

A LangGraph-based AI system for agricultural advice integrated with the existing chat service.

## Features

- **LangGraph Agent**: Intelligent workflow for agricultural query processing
- **Gemini LLM**: Uses Gemini 2.5 Flash for natural language understanding
- **Weather Integration**: Current weather + 3-day forecast with agricultural insights
- **Exa.AI Search**: Agriculture-specific knowledge retrieval
- **MongoDB Storage**: Chat history persistence
- **Streaming Responses**: Real-time response generation
- **Chat Service Integration**: Seamless integration with existing chat infrastructure

## Project Structure

```
backend/
├── src/
│   ├── __init__.py              # Package exports
│   ├── config.py                # Configuration and constants
│   ├── storage.py               # MongoDB storage operations
│   ├── tools.py                 # Weather and knowledge search tools
│   ├── llm_provider.py          # Gemini LLM integration
│   ├── agent.py                 # LangGraph agricultural agent
│   └── agricultural_advisor.py  # Main system and convenience functions
├── chat_service.py              # Simplified chat service with direct agricultural integration
├── requirements.txt             # Dependencies
├── test_agricultural_integration.py  # Integration tests
└── README.md                    # This file
```

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables** (create `.env` file):
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   WEATHERAPI_KEY=your_weather_api_key
   EXA_API_KEY=your_exa_api_key
   MONGODB_URI=mongodb://localhost:27017/
   ```

3. **Start MongoDB** (if using local instance):
   ```bash
   mongod
   ```

## Usage

### Frontend Integration

The `generate_streaming_response` function is designed to be called from your frontend:

```python
# This function is called from frontend
async def generate_streaming_response(message: str, session_id: str, user_location: Optional[Dict] = None):
    """Convenience function for streaming response - called from frontend"""
    system = AgriculturalAssistantSystem(session_id)
    async for chunk, is_complete in system.generate_streaming_response(message, user_location):
        yield chunk, is_complete
```

### Chat Service Integration

The agricultural advisor is directly integrated into the chat service:

```python
from chat_service import ChatService

# Create chat service with session ID
chat_service = ChatService("user_session_123")

# Use agricultural advisor directly
async for chunk, is_complete in chat_service.generate_streaming_response(
    "I have wheat crops and need irrigation advice",
    user_location={"coordinates": {"lat": 40.7128, "lon": -74.0060}}
):
    print(chunk, end="")
    if is_complete:
        break
```

### Direct Usage

You can also use the agricultural advisor directly:

```python
from src.agricultural_advisor import AgriculturalAssistantSystem

# Create system instance
system = AgriculturalAssistantSystem("user_session_123")

# Streaming response
async for chunk, is_complete in system.generate_streaming_response(
    "What pests affect tomato plants?",
    user_location={"coordinates": {"lat": 40.7128, "lon": -74.0060}}
):
    print(chunk, end="")
    if is_complete:
        break

# Complete response
response = await system.generate_complete_response(
    "How to fertilize corn?",
    user_location={"coordinates": {"lat": 40.7128, "lon": -74.0060}}
)
```

## System Architecture

### LangGraph Workflow

1. **Query Analysis**: Extracts crop type and issue type
2. **Weather Context**: Fetches current weather and forecast
3. **Knowledge Retrieval**: Searches Exa.AI for agricultural best practices
4. **Advice Generation**: Combines all information into comprehensive advice

### Supported Crops

- Wheat, Rice, Corn/Maize, Tomato, Potato
- Cabbage, Cotton, Sugarcane, Onion

### Supported Issues

- **Irrigation**: Water management and scheduling
- **Pest Control**: Insect and pest management
- **Disease**: Plant disease prevention and treatment
- **Fertilizer**: Nutrient management and application

## Testing

Run the integration test:

```bash
python test_agricultural_integration.py
```

This will test:
- Agricultural streaming responses
- Agricultural complete responses
- Non-agricultural query handling
- Provider availability

## API Keys Required

- **Gemini API**: For LLM responses
- **WeatherAPI**: For weather data and forecasts
- **Exa.AI**: For agricultural knowledge search
- **MongoDB**: For chat history storage (optional)

## Example Queries

- "I have wheat crops and need irrigation advice"
- "What pests affect tomato plants?"
- "How to prevent disease in rice crops?"
- "Fertilizer recommendations for corn"
- "Weather-based spraying advice for cotton"

## Integration Notes

- The agricultural advisor is directly integrated into the chat service
- No multiple providers - single, streamlined approach
- Fallback responses if agricultural advisor is not available
- All responses are automatically saved to MongoDB
- Location data is optional but enhances weather-based advice
- Non-agricultural queries are handled by Gemini with agricultural context

## Error Handling

- Graceful fallback when APIs are unavailable
- MongoDB connection failures don't break the system
- Missing environment variables are handled gracefully
- Agricultural advisor unavailable shows fallback message 