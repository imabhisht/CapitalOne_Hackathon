from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from chainlit.utils import mount_chainlit
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import json
import os
import sys
import logging

# Import Models
from src.models.chat_request import ChatRequest, ChatResponse

# Import our services
from src.services.chat_service import chat_service
from src.infrastructure.mongo_service import mongo_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to handle startup and shutdown events"""
    
    # Startup
    logger.info("Starting application...")
    
    # Check environment variables
    mongodb_uri = os.getenv("MONGODB_URI")
    required_env_vars = ["MONGODB_URI"]  # Add other required vars as needed
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.info("Application will continue but some features may be limited")
    
    # Initialize MongoDB if URI exists
    if mongodb_uri:
        try:
            await mongo_service.initialize(mongodb_uri)
            logger.info("MongoDB initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB: {e}")
            # Decide whether to continue or exit based on your requirements
            # sys.exit(1)  # Uncomment to exit on MongoDB failure
    else:
        logger.warning("MONGODB_URI not found. MongoDB service not initialized.")
    
    # Check if required directories exist
    static_dir = "static"
    if not os.path.exists(static_dir):
        logger.error(f"Static directory '{static_dir}' not found")
        # You might want to create it or exit
        # os.makedirs(static_dir, exist_ok=True)
    
    # Check if required files exist
    index_file = "static/index.html"
    if not os.path.exists(index_file):
        logger.warning(f"Index file '{index_file}' not found")
    
    chainlit_app = "./src/ui/my_cl_app.py"
    if not os.path.exists(chainlit_app):
        logger.warning(f"Chainlit app '{chainlit_app}' not found")
    
    # Initialize chat service if needed
    try:
        # Add any initialization logic for chat_service here
        logger.info("Chat service ready")
    except Exception as e:
        logger.error(f"Failed to initialize chat service: {e}")
        # sys.exit(1)  # Uncomment to exit on chat service failure
    
    logger.info("Application startup complete")
    
    yield  # This is where the application runs
    
    # Shutdown
    logger.info("Shutting down application...")
        
    # Add any other cleanup logic here
    logger.info("Application shutdown complete")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Streaming Chat API",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_index():
    """Serve the main index page"""
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "mongodb": "connected" if mongo_service.is_connected() else "disconnected",
        "chat_service": "ready"
    }
    return health_status

@app.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """Stream response using the chat service"""
    
    async def generate_stream():
        try:
            async for content_chunk, is_complete in chat_service.generate_streaming_response(request=request):
                # Create response chunk
                chunk = {
                    "content": content_chunk,
                    "is_complete": is_complete
                }
                
                # Send the chunk as JSON
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            error_chunk = {
                "content": f"Error: {str(e)}",
                "is_complete": True,
                "error": True
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )

# Mount Chainlit (do this after all other routes are defined)
try:
    mount_chainlit(app=app, target="./src/ui/my_cl_app.py", path="/chat")
    logger.info("Chainlit mounted successfully at /chat")
except Exception as e:
    logger.error(f"Failed to mount Chainlit: {e}")