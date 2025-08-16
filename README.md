# Agriculture AI Assistant

An AI-powered assistant for agriculture data analysis and insights, built with FastAPI, LangGraph agents, and MongoDB. Provides intelligent responses about agricultural data including crop production, weather patterns, irrigation sources, and temperature data across Indian districts.

## 🚀 Features

- **Multi-Agent System**: LangGraph-powered agents with tool calling capabilities
- **OpenAI-Compatible LLM**: Supports multiple LLM providers (Gemini, OpenAI, Claude, local models)
- **Intelligent LLM Routing**: Automatic routing between small/fast and large/complex models
- **Modern Streamlit UI**: Interactive chat interface with real-time streaming
- **OpenAI API Compatibility**: Full OpenAI API-compatible endpoints
- **Real-time Chat**: Streaming responses with FastAPI integration
- **Production-Ready Server**: Uvicorn ASGI server for high-performance deployment
- **HTTP Client Integration**: Built-in requests library for external API calls
- **LLM Observability**: OpenLit integration for monitoring and analytics
- **Agriculture Data**: Comprehensive district-level data for Indian agriculture
- **Tool Integration**: Weather, location, and calculation tools

## 📁 Project Structure

```
├── backend/                    # Main backend application
│   ├── src/
│   │   ├── agents/            # Multi-agent system and tools
│   │   ├── config/           # Configuration management
│   │   ├── infrastructure/    # MongoDB service layer
│   │   ├── llm/              # OpenAI-compatible LLM integration
│   │   ├── models/           # Data models and schemas
│   │   ├── services/         # Business logic services
│   │   ├── ui/               # Streamlit UI components
│   │   └── workflow/         # Multi-agent workflows
│   ├── app.py               # FastAPI application entry point
│   ├── main.py              # Application launcher
│   ├── test_full_flow.py    # Integration tests
│   └── pyproject.toml       # Python dependencies
└── data/                    # Agriculture datasets and processing
    ├── *.csv               # Raw agriculture data files
    ├── data_loader.py      # MongoDB data loading script
    └── add_geolocation.py  # Geolocation enrichment script
```

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.11+
- MongoDB (local or remote)
- LLM API key (OpenAI, Gemini, Claude via OpenRouter, or other OpenAI-compatible provider)
- Google Maps API key (optional, for enhanced geocoding)

### Key Dependencies

The project includes these essential components:
- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: Lightning-fast ASGI server for production deployment
- **Streamlit**: Interactive web UI for chat interface
- **LangChain/LangGraph**: Multi-agent orchestration and tool calling
- **OpenAI SDK**: LLM integration with multiple provider support
- **MongoDB**: Document database with Motor async driver
- **Requests**: HTTP client for external API integrations
- **OpenLit**: LLM observability and performance monitoring
- **Colorlog**: Enhanced logging with color-coded output for development

### Development Features

- **Enhanced Logging**: Colored console output with structured formatting for improved debugging experience
  - Custom log formatter with color-coded severity levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Detailed logging with filename and line numbers for precise debugging
  - Structured log format: `timestamp - logger_name - level - message (filename:line_number)`
  - Uses colorlog library for enhanced development visibility
- **Real-time Monitoring**: Comprehensive logging across all components with customizable log levels
- **Development Tools**: Built-in test scripts and debugging endpoints for system validation

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your API keys and configuration.

4. **Start the application:**
   ```bash
   # Run both FastAPI backend and Streamlit UI
   python main.py
   
   # Or run separately:
   # Backend API: python app.py
   # Streamlit UI: python run_streamlit.py
   ```

### Data Setup

1. **Navigate to data directory:**
   ```bash
   cd data
   ```

2. **Configure data environment:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your MongoDB URL and API keys.

3. **Load agriculture data:**
   ```bash
   python data_loader.py
   ```

4. **Add geolocation data:**
   ```bash
   python add_geolocation.py
   ```

## ⚙️ Configuration

### Environment Variables

- `USE_MULTI_AGENT`: Enable/disable multi-agent system (default: true)
- `LLM_MODEL`: LLM model to use (default: gpt-3.5-turbo)
- `LLM_API_KEY`: Required for LLM functionality
- `LLM_BASE_URL`: API endpoint for LLM provider
- `MONGODB_URI`: Database connection string
- `PORT`: Server port (default: 5050)
- `GOOGLE_MAPS_API_KEY`: Optional for enhanced geocoding

### Observability & Monitoring

The system includes OpenLit for comprehensive LLM observability:
- **Performance Tracking**: Monitor response times and token usage
- **Cost Analysis**: Track API costs across different providers
- **Error Monitoring**: Capture and analyze LLM failures
- **Usage Analytics**: Understand query patterns and agent performance

**OpenLit Configuration:**
```python
# Automatically checks availability and initializes in app.py
try:
    import requests
    response = requests.get('http://127.0.0.1:4318', timeout=1)
    if response.status_code == 200:
        openlit.init(otlp_endpoint="http://127.0.0.1:4318")
except Exception:
    # Monitoring disabled if endpoint unavailable
    pass
```

**Monitoring Dashboard:**
- Default endpoint: http://127.0.0.1:4318
- Automatically enabled when OpenLit server is running
- Gracefully disabled if monitoring server is unavailable
- Tracks all LLM calls across agents and services
- Provides real-time metrics and cost analysis
- Integrates with popular observability platforms

**Enhanced Development Logging:**
- Color-coded log levels for easy visual debugging
- Structured format with precise source location tracking
- Customizable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Improved readability with timestamp and context information

**Starting OpenLit Monitoring:**
1. Install OpenLit server (if not already running)
2. Start the monitoring server on port 4318
3. The application will automatically detect and connect to it
4. If unavailable, the app continues without monitoring

**Development Logging Configuration:**
The application uses enhanced logging with colorlog that provides:
- Color-coded output for different log levels (cyan for DEBUG, white for INFO, yellow for WARNING, red for ERROR/CRITICAL)
- Structured format: `timestamp - logger_name - level - message (filename:line_number)`
- Console handler with INFO level for comprehensive development visibility
- Improved debugging experience with precise source location tracking

Configure additional OpenLit settings by modifying the initialization in `backend/app.py` or setting environment variables as needed for your monitoring infrastructure.

### Supported LLM Providers

The system supports any OpenAI-compatible API:
- **OpenAI**: Use `https://api.openai.com/v1` as base URL
- **Gemini**: Use `https://generativelanguage.googleapis.com/v1beta/openai/`
- **OpenRouter**: Use `https://openrouter.ai/api/v1` for Claude, etc.
- **Local models**: Any OpenAI-compatible local server

## 🔧 Access Points

- **Streamlit UI**: http://localhost:8501 (Primary interface)
- **Backend API**: http://localhost:5050
- **API Documentation**: http://localhost:5050/docs
- **Health Check**: http://localhost:5050/health

### Key API Endpoints

**Core Chat Endpoints:**
- `POST /chat/stream` - Streaming chat interface using chat service
- `POST /agents/direct/stream` - Direct multi-agent streaming (bypasses chat service)
- `POST /agents/iterative/stream` - Streaming response from iterative agent

**OpenAI API Compatibility:**
- `GET /v1/models` - OpenAI-compatible models endpoint
- `POST /v1/chat/completions` - OpenAI-compatible chat completions (streaming & non-streaming)

**Agent Management:**
- `GET /agents/info` - Get information about available agents
- `POST /agents/iterative/test` - Test iterative agent functionality
- `POST /routing/analyze` - Analyze routing decision for a message

**System Endpoints:**
- `GET /health` - Health check with service status
- `POST /debug/flow` - Debug endpoint to trace system flow
- `GET /streamlit` - Redirect to Streamlit UI
- `GET /` - Serve main index page

## 🤖 Agent Capabilities

### Multi-Agent Architecture
- **Agent Coordinator**: Intelligent routing between specialized agents
- **Specialized Agents**: Organic farming, financial, weather, and general chat agents
- **Iterative Agent**: Complex problem-solving with controlled iteration loops
- **Tool Integration**: Weather, location, and calculation tools
- **External API Integration**: HTTP client for real-time data fetching

### Available Tools
- **Location Tool**: Get location information for Indian districts
- **Weather Tool**: Retrieve weather data and forecasts (supports external APIs)
- **Calculator Tool**: Perform mathematical calculations
- **HTTP Client**: Make requests to external services and APIs

### External Integration Capabilities
With the integrated `requests` library, agents can:
- **Real-time Weather Data**: Connect to live weather APIs
- **External Data Sources**: Fetch current market prices, news, or agricultural data
- **API Orchestration**: Combine multiple external services for comprehensive responses
- **Data Enrichment**: Enhance responses with real-time information

## 🧪 Testing

Run the test suite:
```bash
cd backend
python test_full_flow.py    # Test complete system flow
```

## 🚀 Deployment

**Development:**
```bash
python main.py  # Runs both FastAPI and Streamlit
```

**Production:**
```bash
uvicorn app:app --host 0.0.0.0 --port 5050 --workers 4
```



## 📊 Data Sources

- **Crop Production**: District-wise crop yield and production data
- **Weather Data**: Temperature (min/max) and precipitation records
- **Irrigation**: Water source and irrigation method statistics
- **Geospatial**: Latitude/longitude coordinates for all districts