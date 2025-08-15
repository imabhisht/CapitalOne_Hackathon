# Agriculture AI Assistant

A comprehensive AI-powered assistant for agriculture data analysis and insights, built with FastAPI, LangGraph agents, and MongoDB. The system provides intelligent responses about agricultural data including crop production, weather patterns, irrigation sources, and temperature data across Indian districts.

## 🚀 Features

- **Multi-Agent System**: LangGraph-powered agents with tool calling capabilities
- **OpenAI-Compatible LLM**: Supports multiple LLM providers (Gemini, OpenAI, Claude, local models) via OpenAI SDK
- **Intelligent LLM Routing**: Automatic routing between small/fast and large/complex models based on query complexity
- **Modern Streamlit UI**: Interactive chat interface with real-time streaming and mobile-responsive design
- **OpenAI API Compatibility**: Full OpenAI API-compatible endpoints for third-party integrations
- **Real-time Chat**: Streaming responses with FastAPI integration
- **Session Management**: Persistent conversation history with automatic session tracking
- **Agriculture Data**: Comprehensive district-level data for Indian agriculture
- **Tool Integration**: Weather, location, and calculation tools for enhanced responses

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
│   ├── static/               # Static web assets
│   ├── app.py               # FastAPI application entry point
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
   cp ".env sample" .env
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
   cp ".env sample" .env
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

### Environment Variables

- `USE_MULTI_AGENT`: Enable/disable multi-agent system (default: true)
- `LLM_MODEL`: LLM model to use (default: gpt-3.5-turbo)
- `LLM_API_KEY`: Required for LLM functionality
- `LLM_BASE_URL`: API endpoint for LLM provider
- `MONGODB_URI`: Database connection string
- `GOOGLE_MAPS_API_KEY`: Optional for enhanced geocoding

### Provider Examples

**OpenAI:**
```env
LLM_MODEL=gpt-4
LLM_API_KEY=your_openai_api_key
LLM_BASE_URL=https://api.openai.com/v1
```

**Gemini:**
```env
LLM_MODEL=gemini-2.5-flash
LLM_API_KEY=your_gemini_api_key
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

**OpenRouter (Claude, etc.):**
```env
LLM_MODEL=anthropic/claude-3-sonnet
LLM_API_KEY=your_openrouter_api_key
LLM_BASE_URL=https://openrouter.ai/api/v1
```

## 🔧 API Endpoints

### Health Check
```http
GET /health
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
```http
GET /v1/models
POST /v1/chat/completions
```

### Access Points
- **Streamlit UI**: http://localhost:8501 (Primary interface)
- **Backend API**: http://localhost:5050
- **API Documentation**: http://localhost:5050/docs
- **Health Check**: http://localhost:5050/health

## 🤖 Agent Capabilities

### Multi-Agent Architecture
- **Agent Coordinator**: Intelligent routing between specialized agents
- **Specialized Agents**: Organic farming, financial, weather, and general chat agents
- **Iterative Agent**: Complex problem-solving with controlled iteration loops
- **Tool Integration**: Weather, location, and calculation tools

### Available Tools
- **Location Tool**: Get location information for Indian districts
- **Weather Tool**: Retrieve weather data and forecasts
- **Calculator Tool**: Perform mathematical calculations

## 🧪 Testing

Run the test suite:
```bash
cd backend
python test_agent.py        # Test agent functionality
python test_langraph.py     # Test LangGraph workflows
python test_iterative_agent.py  # Test iterative reasoning
python simple_test.py       # Basic system tests
```

## 🚀 Deployment

### Local Development
```bash
# Run both services (Recommended)
python main.py

# Or run separately
python app.py              # Backend only
python run_streamlit.py    # Streamlit only
```

### Docker Deployment
```bash
docker-compose up -d
```

## 📊 Data Sources

The system includes comprehensive agriculture data:
- **Crop Production**: District-wise crop yield and production data
- **Weather Data**: Temperature (min/max) and precipitation records
- **Irrigation**: Water source and irrigation method statistics
- **Geospatial**: Latitude/longitude coordinates for all districts

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check the logs in respective directories
- Verify environment variable configuration
- Ensure MongoDB is running and accessible
- Test API endpoints with the health check