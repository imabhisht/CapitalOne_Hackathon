# CapitalOne Agentic Assistant - Streamlit Version

This application has been converted from Chainlit to Streamlit for a better user experience and easier customization.

## Features

- 🤖 Interactive chat interface with AI assistant
- 💬 Real-time streaming responses with typing indicators
- 🌐 HTTP API integration with FastAPI backend
- 🎨 Modern, responsive UI design with custom CSS
- 📱 Mobile-friendly interface
- 🔄 Automatic session management and conversation history
- 🛡️ Robust error handling with user-friendly messages
- 🔗 Backend connectivity detection and troubleshooting
- 🌍 Multi-language support (ready for expansion)

## Quick Start

### Option 1: Run Streamlit Only
```bash
cd backend
python run_streamlit.py
```
The app will be available at: http://localhost:8501

### Option 2: Run Both FastAPI and Streamlit
```bash
cd backend
python main.py
```
- FastAPI: http://localhost:5050
- Streamlit: http://localhost:8501

### Option 3: Run Streamlit Directly
```bash
cd backend
streamlit run src/ui/streamlit_app.py --server.port 8501
```

## Installation

1. Install dependencies:
```bash
# Using pip
pip install -r requirements.txt

# Or using uv (recommended)
uv sync
```

2. Set up environment variables in `.env`:
```
PORT=5050
MONGODB_URI=your_mongodb_connection_string
LLM_MODEL=qwen3:4b
LLM_API_KEY=not_required
LLM_BASE_URL=http://localhost:11434/v1
```

## Key Changes from Chainlit

### Advantages of Streamlit:
- **Better customization**: Full control over UI components and styling
- **Rich widgets**: Built-in support for forms, charts, file uploads, etc.
- **Easier deployment**: Multiple deployment options (Streamlit Cloud, Docker, etc.)
- **Better state management**: More intuitive session state handling
- **Community support**: Larger community and more resources

### Migration Notes:
- Chat history is now managed in Streamlit session state
- Streaming responses work seamlessly with Streamlit's chat interface
- Session management is handled through Streamlit's session state
- Custom CSS styling for better visual appeal

## File Structure

```
backend/
├── src/ui/
│   ├── streamlit_app.py      # Main Streamlit application
│   └── my_cl_app.py          # Old Chainlit app (can be removed)
├── main.py                   # Runs both FastAPI and Streamlit
├── run_streamlit.py          # Runs only Streamlit
├── app.py                    # FastAPI application
└── requirements.txt          # Python dependencies
```

## Customization

The Streamlit app is highly customizable:

- **Styling**: Modify the CSS in the `st.markdown()` sections
- **Layout**: Adjust the sidebar, main content, and chat interface
- **Components**: Add new Streamlit widgets and components
- **Themes**: Streamlit supports light/dark themes automatically

## Deployment

### Streamlit Cloud
1. Push your code to GitHub
2. Connect your repository to Streamlit Cloud
3. Deploy with one click

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "src/ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Local Production
```bash
streamlit run src/ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

## Troubleshooting

1. **Port conflicts**: Change the port in the run commands if 8501 is busy
2. **Dependencies**: Make sure all packages are installed with `pip install -r requirements.txt`
3. **Environment**: Ensure your `.env` file is properly configured
4. **MongoDB**: Check your MongoDB connection string and network access

## Next Steps

- Add file upload functionality for document analysis
- Implement user authentication
- Add data visualization components
- Create custom Streamlit components for specialized features
- Add multi-language support
- Implement chat export functionality