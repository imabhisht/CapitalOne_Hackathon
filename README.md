# Agriculture AI Assistant

A comprehensive AI-powered assistant for agriculture data analysis and insights, built with FastAPI, LangGraph agents, and MongoDB. The system provides intelligent responses about agricultural data including crop production, weather patterns, irrigation sources, and temperature data across Indian districts.

## 🚀 Features

- **Multi-Agent System**: LangGraph-powered agents with tool calling capabilities
- **Gemini LLM Integration**: Google Gemini 2.0 Flash model via OpenAI SDK compatibility
- **Real-time Chat**: Streaming responses with FastAPI and Chainlit integration
- **Session Management**: Persistent conversation history with automatic session tracking
- **Agriculture Data**: Comprehensive district-level data for Indian agriculture
- **Geospatial Queries**: Location-based data analysis with MongoDB geospatial indexes
- **Tool Integration**: Weather, location, and calculation tools for enhanced responses
- **RESTful API**: FastAPI backend with health checks and CORS support

## 📁 Project Structure

```
├── backend/                    # Main backend application
│   ├── src/
│   │   ├── agents/            # LangGraph agents and tools
│   │   │   ├── langraph_agent.py      # Main agent implementation
│   │   │   └── tools/                 # Tool registry and implementations
│   │   ├── infrastructure/    # MongoDB service layer
│   │   ├── llm/              # Gemini LLM integration
│   │   │   └── gemini_llm.py         # Gemini API wrapper
│   │   ├── models/           # Data models and schemas
│   │   ├── services/         # Business logic services
│   │   │   └── chat_service.py       # Main chat orchestration
│   │   ├── ui/               # Chainlit UI components
│   │   └── workflow/         # Multi-agent workflows
│   ├── static/               # Static web assets
│   ├── app.py               # FastAPI application entry point
│   └── pyproject.toml       # Python dependencies
└── data/                    # Agriculture datasets and processing
    ├── *.csv               # Raw agriculture data files
    ├── data_loader.py      # MongoDB data loading script
    └── add_geolocation.py  # Geolocation enrichment script
```

## 🏗️ Architecture Overview

### Core Components

1. **FastAPI Application** (`app.py`): Main web server with health checks and CORS
2. **Chat Service** (`chat_service.py`): Orchestrates LLM calls and session management
3. **LangGraph Agent** (`langraph_agent.py`): Multi-agent workflow with tool calling
4. **Gemini LLM** (`gemini_llm.py`): Google Gemini API integration via OpenAI SDK
5. **MongoDB Service** (`mongo_service.py`): Database operations and session storage
6. **Chainlit UI** (`my_cl_app.py`): Interactive chat interface

### Data Flow

1. User sends message via Chainlit UI or API
2. Chat service creates/loads session and stores user message
3. LangGraph agent processes message with conversation history
4. Agent determines if tools are needed and executes them
5. Gemini LLM generates response based on context and tool results
6. Response is streamed back to user and stored in session

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.11+
- MongoDB (local or remote)
- Google Gemini API key
- Google Maps API key (optional, for enhanced geocoding)

### Backend Setup

1. **Navigate to backend directory:**

   ```bash
   cd backend
   ```

2. **Install dependencies:**

   ```bash
   pip install -e .
   ```

   Key dependencies include:

   - `chainlit>=2.6.5` - Interactive chat UI
   - `fastapi[standard]>=0.116.1` - Web framework
   - `langchain-core>=0.3.72` - LangChain core components
   - `langgraph>=0.6.3` - Multi-agent workflows
   - `motor>=3.3.0` - Async MongoDB driver
   - `openai>=1.98.0` - OpenAI SDK (used for Gemini API)
   - `pymongo>=4.14.0` - MongoDB driver
   - `python-dotenv>=1.1.1` - Environment variable management

3. **Configure environment variables:**

   ```bash
   cp .env\ sample .env
   ```

   Edit `.env` with your configuration:

   ```env
   MONGODB_URI=mongodb://localhost:27017/
   GEMINI_API_KEY=your_gemini_api_key
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key  # Optional
   ```

4. **Start the application:**
   ```bash
   python app.py
   ```

### Data Setup

1. **Navigate to data directory:**

   ```bash
   cd data
   ```

2. **Configure data environment:**

   ```bash
   cp .env\ sample .env
   ```

3. **Load agriculture data:**

   ```bash
   python data_loader.py
   ```

4. **Add geolocation data:**
   ```bash
   python add_geolocation.py
   ```

## 🔧 API Endpoints

### Health Check

```http
GET /health
```

Returns system health status including MongoDB connection.

### Streaming Chat

```http
POST /chat/stream
Content-Type: application/json

{
  "message": "What's the weather in Baroda?",
  "session_id": "optional-session-id"
}
```

### Chainlit UI

```http
GET /chat
```

Access the interactive chat interface with persistent session management. The UI automatically:

- Creates new chat sessions for first-time users
- Maintains conversation history across messages
- Tracks session IDs for seamless conversation continuity

## 🤖 Agent Capabilities

The LangGraph agent system includes:

### LLM Integration

- **Gemini 2.0 Flash**: Latest Google Gemini model via OpenAI SDK compatibility
- **Streaming Responses**: Word-by-word streaming for real-time interaction
- **Context Management**: Maintains conversation history across sessions

### Available Tools

- **Location Tool**: Get location information for Indian districts
- **Weather Tool**: Retrieve weather data and forecasts
- **Calculator Tool**: Perform mathematical calculations
- **Debug Logging**: Enhanced tool visibility for development

### Tool Usage Examples

The agent automatically detects when to use tools based on user queries:

- "What's the weather in Baroda?" → Uses weather tool
- "Calculate 25 \* 4 + 10" → Uses calculator tool
- "Where is Jamjodhpur located?" → Uses location tool

### Agent Architecture

- **StateGraph Workflow**: Proper LangGraph implementation with state management
- **Tool Call Detection**: Regex-based tool call extraction from LLM responses
- **Error Handling**: Graceful error recovery and user feedback
- **Conditional Routing**: Smart routing between model calls and tool execution

### Session Management

The Chainlit UI provides seamless conversation continuity:

- **Automatic Session Creation**: New sessions are created for first-time users
- **Session ID Tracking**: Session IDs are automatically stored and reused for conversation continuity
- **Conversation History**: Previous messages are maintained across the session
- **Visual Feedback**: Enhanced console logging shows session creation and reuse with clear indicators (🔗 for new sessions, 🔄 for existing sessions)

## 📊 Data Sources

The system includes comprehensive agriculture data:

- **Crop Production**: District-wise crop yield and production data
- **Weather Data**: Temperature (min/max) and precipitation records
- **Irrigation**: Water source and irrigation method statistics
- **Geospatial**: Latitude/longitude coordinates for all districts

## 🧪 Testing

Run the test suite to verify functionality:

```bash
cd backend
python test_agent.py        # Test agent functionality
python test_langraph.py     # Test LangGraph workflows
python simple_test.py       # Basic system tests
```

## 🔍 Development & Debugging

### Agent Debugging

The LangGraph agent includes enhanced debugging capabilities:

- Tool descriptions are logged during initialization
- Tool execution results are tracked
- State transitions are monitored

### Session Management Debugging

The Chainlit UI includes visual feedback for session management:

- 🔗 indicator when new sessions are created and stored
- 🔄 indicator when existing sessions are reused
- Session IDs are logged for debugging conversation continuity

### Logs

- Application logs: Console output with structured logging
- Data loading: `data/dataloading.log`
- Geocoding: `data/geocoding.log`

## 🚀 Deployment

### Local Development

```bash
# Backend
cd backend && python app.py

# Access at:
# - API: http://localhost:8000
# - Chat UI: http://localhost:8000/chat
# - Health: http://localhost:8000/health
```

### Production Considerations

- Set appropriate CORS origins in `app.py`
- Use environment-specific MongoDB URIs
- Configure proper logging levels
- Set up monitoring for health endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

- Check the logs in respective directories
- Verify environment variable configuration
- Ensure MongoDB is running and accessible
- Test API endpoints with the health check

## 🧠 LLM Integration

### Gemini LLM Implementation

The system uses Google's Gemini 2.5 Flash model through OpenAI SDK compatibility:

- **Model**: `gemini-2.5-flash` (configurable)
- **API Endpoint**: `https://generativelanguage.googleapis.com/v1beta/openai/`
- **Message Format**: Converts LangChain messages to OpenAI format
- **Error Handling**: Graceful fallback for API failures
- **Temperature Control**: Configurable response creativity (default: 0.7)

### Configuration

```python
# Initialize Gemini LLM
llm = GeminiLLM(
    model="gemini-2.5-flash",  # or "gemini-1.5-pro"
    api_key=os.getenv("GEMINI_API_KEY")
)
```

## 🔄 Recent Updates

- **Gemini LLM Integration**: Added Google Gemini 2.5 Flash model support via OpenAI SDK compatibility
- **Enhanced Session Management**: Improved Chainlit UI with automatic session ID tracking and persistent conversation history
- **LangGraph Agent Improvements**: Enhanced tool debugging with description logging for better development visibility
- **Tool Call Detection**: Implemented regex-based tool call extraction for reliable tool execution
- **Conversation Continuity**: Seamless chat experience with proper session handling across multiple messages
- **Error Handling**: Improved error handling and state management throughout the system
- **Documentation**: Updated documentation for better developer experience and accurate setup instructions
