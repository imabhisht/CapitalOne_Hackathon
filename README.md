# Agriculture AI Assistant

A comprehensive AI-powered assistant for agriculture data analysis and insights, built with FastAPI, LangGraph agents, and MongoDB. The system provides intelligent responses about agricultural data including crop production, weather patterns, irrigation sources, and temperature data across Indian districts.

## 🚀 Features

- **Multi-Agent System**: LangGraph-powered agents with tool calling capabilities
- **OpenAI-Compatible LLM**: Supports multiple LLM providers (Gemini, OpenAI, Claude, local models) via OpenAI SDK
- **Intelligent LLM Routing**: Automatic routing between small/fast and large/complex models based on query complexity
- **OpenAI API Compatibility**: Full OpenAI API-compatible endpoints for third-party integrations
- **Modern Streamlit UI**: Interactive chat interface with real-time streaming, custom styling, and mobile-responsive design
- **Multiple Chat Interfaces**: 
  - **Streamlit**: Primary modern chat interface with advanced features
  - **Open WebUI**: Alternative ChatGPT-like interface with file uploads and multi-user support
- **Real-time Chat**: Streaming responses with FastAPI integration
- **Session Management**: Persistent conversation history with automatic session tracking
- **Agriculture Data**: Comprehensive district-level data for Indian agriculture
- **Geospatial Queries**: Location-based data analysis with MongoDB geospatial indexes
- **Tool Integration**: Weather, location, and calculation tools for enhanced responses
- **RESTful API**: FastAPI backend with health checks and CORS support
- **Third-Party Integration**: Compatible with Open WebUI and other OpenAI API clients

## 📁 Project Structure

```
├── backend/                    # Main backend application
│   ├── src/
│   │   ├── agents/            # Multi-agent system and tools
│   │   │   ├── base_agent.py          # Abstract base class for all agents
│   │   │   ├── langraph_agent.py      # LangGraph workflow implementation
│   │   │   ├── iterative_agent.py     # Iterative reasoning agent with controlled loops
│   │   │   ├── intent_gathering_agent.py  # Intent clarification agent
│   │   │   ├── agent_coordinator.py   # Multi-agent coordination and routing
│   │   │   ├── organic_farming_agent.py   # Organic farming specialist
│   │   │   ├── financial_agent.py     # Financial advice specialist
│   │   │   ├── weather_agent.py       # Weather information specialist
│   │   │   ├── general_chat_agent.py  # General conversation handler
│   │   │   └── tools/                 # Tool registry and implementations
│   │   ├── config/           # Configuration management
│   │   │   ├── __init__.py           # Configuration module exports
│   │   │   └── multi_agent_config.py # Multi-agent system configuration
│   │   ├── infrastructure/    # MongoDB service layer
│   │   ├── llm/              # OpenAI-compatible LLM integration
│   │   │   └── openai_compatible_llm.py  # Generic LLM wrapper
│   │   ├── models/           # Data models and schemas
│   │   ├── services/         # Business logic services
│   │   │   ├── chat_service.py       # Main chat orchestration
│   │   │   ├── multi_agent_service.py # Multi-agent service layer
│   │   │   └── routing_service.py    # Intelligent LLM routing service
│   │   ├── ui/               # Streamlit UI components
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
3. **Multi-Agent Service** (`multi_agent_service.py`): Service layer for multi-agent system coordination
4. **Routing Service** (`routing_service.py`): Intelligent routing between different LLM models based on query complexity
5. **Agent Coordinator** (`agent_coordinator.py`): Routes queries to appropriate specialized agents
6. **Base Agent** (`base_agent.py`): Abstract base class providing common agent functionality
7. **Specialized Agents**: Domain-specific agents (organic farming, financial, weather, general chat)
8. **LangGraph Agent** (`langraph_agent.py`): Multi-agent workflow with tool calling
9. **Iterative Agent** (`iterative_agent.py`): Controlled iterative reasoning agent for complex problem-solving
10. **Intent Gathering Agent** (`intent_gathering_agent.py`): Clarifies user intent through conversation
10. **Multi-Agent Config** (`multi_agent_config.py`): Configuration management for the multi-agent system
11. **OpenAI-Compatible LLM** (`openai_compatible_llm.py`): Generic LLM wrapper supporting multiple providers via OpenAI SDK
12. **MongoDB Service** (`mongo_service.py`): Database operations and session storage
13. **Streamlit UI** (`streamlit_app.py`): Modern interactive chat interface with real-time streaming

### Data Flow

1. User sends message via Streamlit UI or API
2. Chat service creates/loads session and stores user message
3. LangGraph agent processes message with conversation history
4. Agent determines if tools are needed and executes them
5. LLM generates response based on context and tool results
6. Response is streamed back to user and stored in session

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.11+
- MongoDB (local or remote)
- LLM API key (OpenAI, Gemini, Claude via OpenRouter, or other OpenAI-compatible provider)
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

   - `streamlit>=1.28.0` - Modern interactive web UI framework (migrated from Chainlit)
   - `fastapi[standard]>=0.116.1` - Web framework
   - `langchain-core>=0.3.72` - LangChain core components
   - `langgraph>=0.6.3` - Multi-agent workflows
   - `motor>=3.3.0` - Async MongoDB driver
   - `openai>=1.98.0` - OpenAI SDK (used for all LLM providers)
   - `pymongo>=4.14.0` - MongoDB driver
   - `python-dotenv>=1.1.1` - Environment variable management

3. **Configure environment variables:**

   ```bash
   cp .env\ sample .env
   ```

   Edit `.env` with your configuration:

   ```env
   MONGODB_URI=mongodb://localhost:27017/
   LLM_MODEL=gpt-3.5-turbo
   LLM_API_KEY=your_api_key
   LLM_BASE_URL=https://api.openai.com/v1
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key  # Optional
   USE_MULTI_AGENT=true  # Enable multi-agent system
   ```

4. **Start the applications:**

   **Option 1: Run both services together:**
   ```bash
   python main.py
   ```

   **Option 2: Run services separately:**
   
   Backend API:
   ```bash
   python app.py
   ```
   
   Streamlit UI (in a separate terminal):
   ```bash
   python run_streamlit.py
   # OR
   streamlit run src/ui/streamlit_app.py --server.port 8501
   ```

   **Option 3: Run Streamlit only:**
   ```bash
   python run_streamlit.py
   ```

### Open WebUI Setup (Alternative Chat Interface)

For a modern, ChatGPT-like interface with advanced features:

1. **Quick Setup with Docker:**
   ```bash
   ./setup-openwebui.sh
   ```

2. **Standalone Installation:**
   ```bash
   ./setup-openwebui-standalone.sh
   ```

3. **Manual Setup:**
   ```bash
   pip install open-webui
   export OPENAI_API_BASE_URL="http://localhost:5050/v1"
   export OPENAI_API_KEY="not_required"
   open-webui serve --port 3000
   ```

**Access Points:**
- Streamlit UI: http://localhost:8501 (modern interactive interface)
- Open WebUI: http://localhost:3000 (ChatGPT-like interface)
- API Docs: http://localhost:5050/docs

See [OPENWEBUI_SETUP.md](OPENWEBUI_SETUP.md) for detailed setup instructions.

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

## ⚙️ Configuration

The system uses a centralized configuration management approach via the `MultiAgentConfig` class:

### Configuration Options

- **Agent Control**: Enable/disable specific agents
- **Parallel Processing**: Configure multi-agent parallel execution
- **LLM Settings**: Provider selection, model, temperature, token limits
- **Response Settings**: Streaming delays, conversation history limits
- **Environment Integration**: Environment variable overrides

### Configuration Access

```python
from src.config import MultiAgentConfig

# Get complete configuration
config = MultiAgentConfig.get_config()

# Check specific settings
if MultiAgentConfig.is_agent_enabled("organic_farming"):
    print("Organic farming agent is enabled")

# Validate configuration
issues = MultiAgentConfig.validate_config()
if issues:
    print(f"Configuration issues found: {issues}")
```

### Environment Variables

The system respects these environment variables:

- `USE_MULTI_AGENT`: Enable/disable multi-agent system (default: true)
- `LLM_MODEL`: LLM model to use (default: gpt-3.5-turbo)
- `LLM_API_KEY`: Required for LLM functionality
- `LLM_BASE_URL`: API endpoint for LLM provider
- `MONGODB_URI`: Database connection string
- `GOOGLE_MAPS_API_KEY`: Optional for enhanced geocoding

## 🔧 API Endpoints

### Health Check

```http
GET /health
```

Returns system health status including MongoDB connection.

### Agents Info

```http
GET /agents/info
```

Get information about available agents and their capabilities.

Response example:
```json
{
  "organic_farming": {
    "name": "Organic Farming Guide",
    "keywords": ["organic", "farming", "agriculture", "crop", "soil"],
    "description": "Specialized in organic farming"
  },
  "financial": {
    "name": "Financial Advisor", 
    "keywords": ["finance", "money", "budget", "investment"],
    "description": "Specialized in financial"
  }
}
```

### Streaming Chat

```http
POST /chat/stream
Content-Type: application/json

{
  "message": "What's the weather in Baroda?",
  "session_id": "optional-session-id"
}
```

### OpenAI API Compatibility

The backend now provides OpenAI-compatible endpoints for integration with third-party tools like Open WebUI:

#### List Models

```http
GET /v1/models
```

Returns available models in OpenAI API format:
```json
{
  "object": "list",
  "data": [
    {
      "id": "agriculture-ai-assistant",
      "object": "model",
      "created": 1677610602,
      "owned_by": "agriculture-ai"
    }
  ]
}
```

#### Chat Completions

```http
POST /v1/chat/completions
Content-Type: application/json

{
  "model": "agriculture-ai-assistant",
  "messages": [
    {"role": "user", "content": "What's the weather like for farming?"}
  ],
  "stream": false
}
```

**Streaming Support:**
```http
POST /v1/chat/completions
Content-Type: application/json

{
  "model": "agriculture-ai-assistant", 
  "messages": [
    {"role": "user", "content": "How can I improve crop yield?"}
  ],
  "stream": true
}
```

Returns OpenAI-compatible streaming responses with proper SSE formatting.

### Streamlit UI

Access the modern interactive chat interface at `http://localhost:8501` with comprehensive features:

#### Key Features
- **Real-time Streaming**: Word-by-word response streaming with typing indicators for immediate feedback
- **HTTP API Integration**: Communicates with FastAPI backend via HTTP requests for better separation of concerns
- **Session Management**: Persistent conversation history with automatic session tracking and generation
- **Modern Interface**: Clean, responsive design with custom CSS styling and gradient headers
- **Mobile-Friendly**: Responsive design that works seamlessly on all devices
- **Settings Panel**: Sidebar with language selection, session info, and chat management controls
- **Robust Error Handling**: Comprehensive error handling with user-friendly messages and recovery suggestions
- **Connection Management**: Automatic detection of backend availability with helpful troubleshooting tips
- **Chat Controls**: Clear chat functionality, session information display, and conversation history

#### UI Components
- **Header**: Branded header with gradient styling and application description
- **Chat Interface**: Streamlit's native chat interface with persistent message history
- **Sidebar**: Settings panel with user session info, language selection, and controls
- **Streaming Display**: Real-time message streaming with visual typing indicators (▌)
- **Custom Styling**: Professional appearance with custom CSS, gradients, and responsive theming
- **Error Messages**: User-friendly error displays with actionable troubleshooting guidance

#### Architecture
- **Decoupled Design**: Streamlit UI communicates with FastAPI backend via HTTP API calls
- **API Integration**: Uses `/chat/stream` endpoint for streaming responses
- **Session Handling**: Automatic session ID generation and management across conversations
- **Connection Resilience**: Graceful handling of backend connectivity issues with clear user feedback

#### Running the Streamlit App
```bash
# Option 1: Using the run script (Streamlit only)
python run_streamlit.py

# Option 2: Direct Streamlit command
streamlit run src/ui/streamlit_app.py --server.port 8501

# Option 3: Run with both FastAPI and Streamlit (Recommended)
python main.py
```

**Important**: The Streamlit app requires the FastAPI backend to be running at `http://localhost:5050` for full functionality. When running separately, ensure both services are started.

#### Advantages over Previous Chainlit Implementation
- **Better Customization**: Full control over UI components and styling
- **Service Separation**: Clean separation between UI and backend services
- **Rich Widgets**: Built-in support for forms, charts, file uploads, and more
- **Easier Deployment**: Multiple deployment options (Streamlit Cloud, Docker, etc.)
- **Better State Management**: More intuitive session state handling with automatic session generation
- **Community Support**: Larger community and extensive documentation
- **Mobile Responsive**: Better mobile experience out of the box
- **Error Recovery**: Comprehensive error handling with user guidance for common issues

## 🤖 Agent Capabilities

The system features a sophisticated multi-agent architecture with specialized agents and intelligent routing:

### Agent Architecture

- **Agent Coordinator**: Enhanced routing system with intelligent mode selection (SIMPLE vs ITERATIVE) and weather query intelligence
- **Base Agent Class**: Abstract base class (`BaseAgent`) providing common functionality for all specialized agents
- **Specialized Agents**: Domain-specific agents inheriting from `BaseAgent`:
  - **Organic Farming Agent**: Specialized in sustainable agriculture practices
  - **Financial Agent**: Handles financial advice, calculations, and planning
  - **Weather Agent**: Provides weather information and agricultural weather guidance
  - **General Chat Agent**: Handles general conversations and non-specialized queries
- **LangGraph Integration**: StateGraph workflow with proper state management
- **Intent Gathering Agent**: Clarifies user intent through conversational interaction
- **Multi-Agent Service**: Service layer that orchestrates the entire multi-agent system
- **Configuration Management**: Centralized configuration via `MultiAgentConfig` class

### Base Agent Features

The `BaseAgent` class provides:
- **Abstract Interface**: Standardized methods for all specialized agents
- **LLM Integration**: Built-in OpenAI-compatible LLM support with conversation history
- **Streaming Support**: Word-by-word response streaming capabilities
- **Error Handling**: Graceful error recovery and user feedback
- **Conversation Management**: Automatic conversation history handling (last 5 messages)

### Iterative Agent

The system includes a sophisticated iterative agent (`iterative_agent.py`) that can solve complex problems through controlled iteration, automatically invoked by the enhanced routing system:

- **Intelligent Routing Integration**: Automatically activated for complex queries, weather queries without location, and real-time data requests
- **Controlled Iteration**: Limits the number of reasoning loops to prevent excessive LLM calls (default: 5 iterations)
- **Step-by-Step Reasoning**: Follows a structured THOUGHT → ACTION → OBSERVATION pattern
- **Tool Integration**: Can call tools strategically during the reasoning process
- **Streaming Support**: Provides real-time updates during each iteration step
- **Final Answer Detection**: Automatically detects when sufficient information is gathered
- **Error Recovery**: Graceful handling of tool failures and iteration limits
- **Conversation Context**: Maintains conversation history throughout the iterative process

#### Iterative Agent Features

- **IterationStep Tracking**: Each step includes thought process, actions taken, and observations
- **Strategic Tool Usage**: Only calls tools when necessary to solve the problem
- **Maximum Iteration Control**: Prevents infinite loops with configurable iteration limits
- **Clean Streaming Experience**: Minimal progress indicators with word-by-word final answer delivery
- **Response Parsing**: Intelligent parsing of LLM responses for THOUGHT, ACTION, and FINAL_ANSWER
- **Tool Execution**: Safe tool execution with error handling and fallback strategies

#### Usage Examples

The iterative agent is automatically activated for complex queries that require multiple steps:

- "Analyze the weather patterns and recommend the best crops for maximum profit"
- "What's the weather today?" (automatically detects need for location and gets current weather)
- "Calculate the irrigation costs and determine the optimal planting schedule"
- "Research organic farming methods and create a financial plan for implementation"
- "Is it good weather for planting tomatoes?" (gets location, weather, and provides analysis)

### LLM Integration

- **Multi-Provider Support**: Works with any OpenAI SDK-compatible LLM provider
- **Flexible Configuration**: Easy switching between providers via environment variables
- **Streaming Responses**: Word-by-word streaming for real-time interaction
- **Context Management**: Maintains conversation history across sessions
- **Message Format**: LangChain message format with system, human, and AI messages

### Available Tools

- **Location Tool**: Get location information for Indian districts
- **Weather Tool**: Retrieve weather data and forecasts
- **Calculator Tool**: Perform mathematical calculations
- **Enhanced Tool Registry**: Improved LangChain tool compatibility with flexible invocation patterns and fixed empty parameter handling
- **Debug Logging**: Enhanced tool visibility for development

### Tool Usage Examples

The agent automatically detects when to use tools based on user queries:

- "What's the weather in Baroda?" → Uses weather tool
- "Calculate 25 \* 4 + 10" → Uses calculator tool
- "Where is Jamjodhpur located?" → Uses location tool

### Agent Workflow

- **StateGraph Workflow**: Proper LangGraph implementation with state management
- **Tool Call Detection**: Regex-based tool call extraction from LLM responses
- **Intent Clarification**: Multi-turn conversations to gather complete user intent
- **Conditional Routing**: Smart routing between model calls and tool execution

### Session Management

The Streamlit UI provides seamless conversation continuity:

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
python test_iterative_agent.py  # Test iterative reasoning agent
python test_routing_service.py  # Test intelligent LLM routing
python simple_test.py       # Basic system tests
python test_conversation_history.py  # Test conversation history functionality
```

All test files use the standardized environment variables (`LLM_MODEL`, `LLM_API_KEY`, `LLM_BASE_URL`) for consistent multi-provider LLM support.

## 🔍 Development & Debugging

### Agent Debugging

The LangGraph agent includes enhanced debugging capabilities:

- Tool descriptions are logged during initialization
- Tool execution results are tracked
- State transitions are monitored

### Session Management Debugging

The Streamlit UI includes visual feedback for session management:

- 🔗 indicator when new sessions are created and stored
- 🔄 indicator when existing sessions are reused
- Session IDs are logged for debugging conversation continuity

### Logs

- Application logs: Console output with structured logging
- Data loading: `data/dataloading.log`
- Geocoding: `data/geocoding.log`

## 🚀 Deployment

### Local Development

**Option 1: Run both services together (Recommended):**
```bash
cd backend && python main.py
```
This starts both FastAPI backend and Streamlit UI simultaneously.

**Option 2: Run services separately:**
```bash
# Backend API (Terminal 1)
cd backend && python app.py

# Streamlit UI (Terminal 2) 
cd backend && python run_streamlit.py
```
Use this option for development when you need to restart services independently.

**Option 3: Streamlit only (Limited functionality):**
```bash
cd backend && python run_streamlit.py
```
**Note**: This will show connection errors since the Streamlit app requires the FastAPI backend for chat functionality.

**Access Points:**
- Streamlit UI: http://localhost:8501 (Modern chat interface - requires backend)
- Backend API: http://localhost:5050 (REST API)
- Health Check: http://localhost:5050/health
- OpenAI API: http://localhost:5050/v1/models
- API Documentation: http://localhost:5050/docs

**Development Tips:**
- Always run both services for full functionality
- The Streamlit app will display helpful error messages if the backend is not available
- Use Option 2 for development to restart services independently
- Check the health endpoint to verify backend connectivity

### Docker Deployment

The project includes Docker Compose configuration with Open WebUI integration:

```bash
# Start all services
docker-compose up -d

# Access at:
# - Backend API: http://localhost:5050
# - Open WebUI: http://localhost:3000
# - Chat UI: http://localhost:5050/chat
```

**Open WebUI Integration**: The Docker setup includes Open WebUI configured to use the agriculture AI assistant as an OpenAI-compatible backend, providing a modern chat interface with the full power of the multi-agent system.

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

### Intelligent LLM Routing

The system features an intelligent routing service that automatically selects the most appropriate LLM model based on query complexity:

#### Routing Logic
- **Simple Queries**: Routed to small, fast models for quick responses (greetings, basic questions, short responses)
- **Complex Queries**: Routed to larger, more capable models for detailed analysis and complex reasoning
- **Automatic Classification**: Uses pattern matching, keyword analysis, and message length to determine complexity
- **Cost Optimization**: Reduces costs by using smaller models when appropriate
- **Performance Optimization**: Faster responses for simple queries, thorough analysis for complex ones

#### Configuration
The routing service supports dual-model configuration:

```env
# Main LLM for complex tasks
LLM_MODEL=gpt-4
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1

# Small LLM for simple tasks and routing decisions
SMALL_LLM_MODEL=gpt-3.5-turbo
SMALL_LLM_API_KEY=your_api_key
SMALL_LLM_BASE_URL=https://api.openai.com/v1
```

#### Routing Examples
- **Simple**: "Hello", "Thank you", "What's the weather in Mumbai?" → Small model
- **Complex**: "Analyze crop yield trends", "What's the weather today?" (no location), "Write a financial report" → Main model
- **Weather Intelligence**: 
  - "What's the weather in Baroda?" → SIMPLE mode (location specified)
  - "What's the weather today?" → ITERATIVE mode (needs location detection)
  - "Is it good weather for planting?" → ITERATIVE mode (needs location + analysis)

#### Routing Information
The service provides detailed routing information for debugging:
```python
from src.services.routing_service import routing_service

info = routing_service.get_routing_info("How do I optimize crop yields?")
# Returns: classification, confidence, selected_model, etc.
```

### OpenAI-Compatible LLM Implementation

The system uses a generic OpenAI-compatible LLM wrapper that supports multiple providers:

- **Model**: Configurable via `LLM_MODEL` environment variable (default: `gpt-3.5-turbo`)
- **API Key**: Set via `LLM_API_KEY` environment variable
- **Base URL**: Configurable via `LLM_BASE_URL` environment variable for different providers
- **Supported Providers**: Any OpenAI SDK-compatible service (OpenAI, Gemini, Claude via OpenRouter, local models, etc.)
- **Message Format**: Converts LangChain messages to OpenAI format
- **Error Handling**: Graceful fallback for API failures
- **Temperature Control**: Configurable response creativity (default: 0.7)

### Configuration

The multi-agent system is configured via the `MultiAgentConfig` class:

```python
# Import configuration
from src.config import MultiAgentConfig

# Check configuration
config = MultiAgentConfig.get_config()
print(f"Multi-agent enabled: {config['use_multi_agent']}")
print(f"Available agents: {config['agents_enabled']}")

# Validate configuration
issues = MultiAgentConfig.validate_config()
if issues:
    print(f"Configuration issues: {issues}")

# Initialize OpenAI-compatible LLM
from src.llm.openai_compatible_llm import OpenAICompatibleLLM
llm = OpenAICompatibleLLM(
    model=MultiAgentConfig.DEFAULT_MODEL,
    api_key=MultiAgentConfig.LLM_API_KEY,
    base_url=os.getenv("LLM_BASE_URL")
)

# Use the multi-agent service
from src.services.multi_agent_service import multi_agent_service
from src.models.chat_request import ChatRequest

request = ChatRequest(message="What's the weather like for farming?")
async for chunk, is_complete in multi_agent_service.generate_streaming_response(request):
    if not is_complete:
        print(chunk, end="")
```

### Environment Variables

Configure the system via environment variables:

```env
# LLM Configuration (OpenAI-compatible)
USE_MULTI_AGENT=true
LLM_MODEL=gpt-3.5-turbo
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1

# Small LLM for routing and simple tasks (optional)
SMALL_LLM_MODEL=gpt-3.5-turbo
SMALL_LLM_API_KEY=your_api_key
SMALL_LLM_BASE_URL=https://api.openai.com/v1

# Database
MONGODB_URI=mongodb://localhost:27017/

# Optional
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

**Provider Examples**:
- **OpenAI**: `LLM_MODEL=gpt-4`, `LLM_BASE_URL=https://api.openai.com/v1` (or omit for default)
- **Gemini**: `LLM_MODEL=gemini-2.5-flash`, `LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/`
- **OpenRouter (Claude, etc.)**: `LLM_MODEL=anthropic/claude-3-sonnet`, `LLM_BASE_URL=https://openrouter.ai/api/v1`
- **Local Models**: `LLM_MODEL=llama-3`, `LLM_BASE_URL=http://localhost:11434/v1`
- **Other Providers**: Any OpenAI SDK-compatible endpoint

## 🔄 Recent Updates

- **Improved Iterative Agent UX**: Enhanced streaming experience with minimal visual clutter and natural word-by-word final answer delivery
- **Enhanced Agent Routing**: Improved Agent Coordinator with intelligent weather query handling and real-time data detection for better SIMPLE vs ITERATIVE mode selection
- **Iterative Agent**: Added sophisticated iterative reasoning agent (`iterative_agent.py`) with controlled iteration loops, step-by-step problem solving, strategic tool usage, streaming support, and automatic final answer detection for complex multi-step queries
- **Enhanced Tool Registry**: Improved tool registry system with better LangChain compatibility, flexible invocation patterns, fixed empty parameter handling, and unified tool interface through ToolAdapter pattern
- **Intelligent LLM Routing**: Added smart routing service that automatically selects appropriate LLM models based on query complexity for cost and performance optimization
- **Streamlit Architecture Improvement**: Updated Streamlit UI to communicate with FastAPI backend via HTTP API calls for better service separation and deployment flexibility
- **Enhanced Error Handling**: Added comprehensive error handling with user-friendly messages and troubleshooting guidance for backend connectivity issues
- **Robust Session Management**: Improved session handling with automatic session ID generation and persistent conversation history
- **Streamlit Migration**: Migrated from Chainlit to Streamlit for a modern, customizable chat interface with better user experience and mobile responsiveness
- **Enhanced UI Features**: Added custom styling, sidebar controls, session management, and improved error handling
- **Multiple Run Options**: Added convenient scripts for running Streamlit alone or with FastAPI backend
- **OpenAI API Compatibility**: Added full OpenAI API-compatible endpoints (`/v1/models`, `/v1/chat/completions`) for third-party integrations
- **Open WebUI Integration**: Docker Compose setup with Open WebUI for modern chat interface
- **Streaming API Support**: OpenAI-compatible streaming responses with proper SSE formatting
- **Third-Party Tool Support**: Backend now works seamlessly with OpenAI API clients and tools
- **Standardized LLM Configuration**: All test files and components now use the standardized environment variables (`LLM_MODEL`, `LLM_API_KEY`, `LLM_BASE_URL`) for consistent multi-provider support
- **Generic LLM Wrapper**: Refactored `GeminiLLM` to `OpenAICompatibleLLM` for multi-provider support (Gemini, OpenAI, Claude, local models)
- **Flexible Provider Configuration**: Added `LLM_BASE_URL` environment variable for easy switching between LLM providers
- **Environment Variable Configuration**: Updated to use `LLM_MODEL`, `LLM_API_KEY`, and `LLM_BASE_URL` for flexible LLM configuration
- **Configuration Module**: Added centralized configuration management via `MultiAgentConfig` class with proper module exports
- **Multi-Agent Coordination**: Implemented `AgentCoordinator` for intelligent query routing and multi-agent orchestration
- **Specialized Agents**: Added domain-specific agents (organic farming, financial, weather, general chat) with keyword-based routing
- **Parallel Processing**: Support for running multiple agents simultaneously on complex queries
- **Base Agent Architecture**: Introduced `BaseAgent` abstract base class for standardized agent development with streaming support and conversation management
- **Multi-Agent Service**: Service layer for coordinating the entire multi-agent system with streaming responses
- **Intent Gathering**: Added `IntentGatheringAgent` for clarifying user intent through conversational interaction
- **Streaming Support**: Built-in streaming capabilities in the base agent class
- **OpenAI-Compatible LLM Integration**: Unified interface supporting multiple providers through standardized OpenAI SDK format
- **Enhanced Session Management**: Modern Streamlit UI with automatic session ID tracking and persistent conversation history
- **LangGraph Agent Improvements**: Enhanced tool debugging with description logging for better development visibility
- **Tool Call Detection**: Implemented regex-based tool call extraction for reliable tool execution
- **Conversation Continuity**: Seamless chat experience with proper session handling across multiple messages
- **Error Handling**: Improved error handling and state management throughout the system
- **Enhanced Tool Registry**: Improved tool registry system with better LangChain compatibility, flexible invocation patterns, fixed empty parameter handling, and unified tool interface
- **Documentation**: Updated documentation for better developer experience and accurate setup instructions
