from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import json
import os
import sys
import colorlog
import subprocess
import threading
import openlit

# Import Modelsw
from src.models.chat_request import ChatRequest, ChatResponse

# Import our services
from src.services.chat_service import chat_service
from src.services.multi_agent_service import multi_agent_service
from src.infrastructure.mongo_service import mongo_service

# Configure logging
colorlog.basicConfig(level=colorlog.INFO)
logger = colorlog.getLogger(__name__)


# Check if OpenLit endpoint is available before initializing
try:
    import requests
    response = requests.get('http://127.0.0.1:3000', timeout=1)
    if response.status_code == 200:
        openlit.init(
            otlp_endpoint="http://127.0.0.1:4318", 
        )
        logger.info("OpenLit monitoring initialized successfully")
    else:
        logger.info("OpenLit endpoint not available, monitoring disabled")
except Exception as e:
    logger.info(f"OpenLit monitoring not available: {e}")


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
    
    streamlit_app = "./src/ui/streamlit_app.py"
    if not os.path.exists(streamlit_app):
        logger.warning(f"Streamlit app '{streamlit_app}' not found")
    
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
        "chat_service": "ready",
        "multi_agent_service": "available" if multi_agent_service.is_available() else "unavailable"
    }
    return health_status

@app.get("/agents/info")
async def get_agents_info():
    """Get information about available agents"""
    return multi_agent_service.get_agent_info()

@app.post("/routing/analyze")
async def analyze_routing(request: dict):
    """Analyze routing decision for a message"""
    from src.services.routing_service import routing_service
    
    message = request.get("message", "")
    if not message:
        return {"error": "Message is required"}
    
    routing_info = routing_service.get_routing_info(message)
    return {
        "message": message,
        "routing_decision": routing_info,
        "models": {
            "small_model": os.getenv("SMALL_LLM_MODEL", "not configured"),
            "main_model": os.getenv("LLM_MODEL", "not configured")
        }
    }

@app.post("/agents/iterative/test")
async def test_iterative_agent(request: dict):
    """Test the iterative agent functionality"""
    message = request.get("message", "")
    if not message:
        return {"error": "Message is required"}
    
    try:
        # Test routing decision
        routing_decision = await multi_agent_service.coordinator.route_query(message)
        
        # Get agent info
        agent_info = multi_agent_service.get_agent_info()
        
        # Test chat service configuration
        chat_service_config = {
            "use_multi_agent": chat_service.use_multi_agent,
            "use_smart_routing": chat_service.use_smart_routing,
        }
        
        return {
            "message": message,
            "routing_decision": routing_decision,
            "agent_info": agent_info,
            "iterative_available": hasattr(multi_agent_service.coordinator, 'iterative_agent'),
            "max_iterations": getattr(multi_agent_service.coordinator.iterative_agent, 'max_iterations', None) if hasattr(multi_agent_service.coordinator, 'iterative_agent') else None,
            "multi_agent_available": multi_agent_service.is_available(),
            "chat_service_config": chat_service_config
        }
    except Exception as e:
        logger.error(f"Error testing iterative agent: {e}")
        return {"error": str(e)}

@app.post("/agents/iterative/stream")
async def stream_iterative_response(request: dict):
    """Stream response from iterative agent"""
    message = request.get("message", "")
    if not message:
        return {"error": "Message is required"}
    
    async def generate_iterative_stream():
        try:
            if not multi_agent_service.is_available():
                yield f"data: {json.dumps({'error': 'Multi-agent service not available'})}\n\n"
                return
            
            # Use the coordinator's streaming method
            async for chunk, is_complete in multi_agent_service.coordinator.stream_process_query(message):
                response_chunk = {
                    "content": chunk,
                    "is_complete": is_complete
                }
                yield f"data: {json.dumps(response_chunk)}\n\n"
                
        except Exception as e:
            logger.error(f"Error in iterative streaming: {e}")
            error_chunk = {
                "content": f"Error: {str(e)}",
                "is_complete": True,
                "error": True
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate_iterative_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )

@app.post("/agents/direct/stream")
async def stream_direct_multi_agent(request: dict):
    """Stream response directly from multi-agent service (bypassing chat service)"""
    message = request.get("message", "")
    if not message:
        return {"error": "Message is required"}
    
    async def generate_direct_stream():
        try:
            if not multi_agent_service.is_available():
                yield f"data: {json.dumps({'error': 'Multi-agent service not available'})}\n\n"
                return
            
            # Create a ChatRequest and use multi-agent service directly
            from src.models.chat_request import ChatRequest
            chat_request = ChatRequest(message=message)
            
            # Use multi-agent service directly
            async for chunk, is_complete in multi_agent_service.generate_streaming_response(chat_request):
                response_chunk = {
                    "content": chunk,
                    "is_complete": is_complete
                }
                yield f"data: {json.dumps(response_chunk)}\n\n"
                
        except Exception as e:
            logger.error(f"Error in direct multi-agent streaming: {e}")
            error_chunk = {
                "content": f"Error: {str(e)}",
                "is_complete": True,
                "error": True
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate_direct_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )

@app.post("/debug/flow")
async def debug_flow_endpoint(request: dict):
    """Debug endpoint to trace the flow and identify issues"""
    message = request.get("message", "")
    if not message:
        return {"error": "Message is required"}
    
    try:
        debug_info = {
            "message": message,
            "chat_service_config": {
                "use_multi_agent": chat_service.use_multi_agent,
                "use_smart_routing": chat_service.use_smart_routing,
            },
            "multi_agent_available": multi_agent_service.is_available(),
            "coordinator_available": hasattr(multi_agent_service, 'coordinator') and multi_agent_service.coordinator is not None,
            "iterative_agent_available": False,
            "routing_decision": None,
            "error": None
        }
        
        if multi_agent_service.is_available() and hasattr(multi_agent_service, 'coordinator'):
            debug_info["iterative_agent_available"] = hasattr(multi_agent_service.coordinator, 'iterative_agent')
            
            # Test routing
            try:
                routing = await multi_agent_service.coordinator.route_query(message)
                debug_info["routing_decision"] = routing
            except Exception as e:
                debug_info["routing_error"] = str(e)
        
        return debug_info
        
    except Exception as e:
        logger.error(f"Error in debug flow: {e}")
        return {"error": str(e)}

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

# OpenAI API compatibility endpoints for Open WebUI
@app.get("/v1/models")
async def list_models():
    """List available models - OpenAI API compatible"""
    return {
        "object": "list",
        "data": [
            {
                "id": os.getenv("LLM_MODEL", "agriculture-ai-assistant"),
                "object": "model",
                "created": 1677610602,
                "owned_by": "agriculture-ai",
                "permission": [],
                "root": os.getenv("LLM_MODEL", "agriculture-ai-assistant"),
                "parent": None
            }
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: dict):
    """OpenAI-compatible chat completions endpoint"""
    try:
        # Extract the last message from the OpenAI format
        messages = request.get("messages", [])
        if not messages:
            return {"error": "No messages provided"}
        
        # Get the last user message
        last_message = messages[-1]["content"] if messages else ""
        
        # Create our internal chat request
        chat_request = ChatRequest(
            message=last_message,
            session_id=request.get("session_id")
        )
        
        # Check if streaming is requested
        stream = request.get("stream", False)
        
        if stream:
            async def generate_openai_stream():
                try:
                    full_response = ""
                    async for content_chunk, is_complete in chat_service.generate_streaming_response(request=chat_request):
                        if not is_complete:
                            full_response += content_chunk
                            chunk = {
                                "id": "chatcmpl-agriculture-ai",
                                "object": "chat.completion.chunk",
                                "created": 1677610602,
                                "model": os.getenv("LLM_MODEL", "agriculture-ai-assistant"),
                                "choices": [
                                    {
                                        "index": 0,
                                        "delta": {
                                            "content": content_chunk
                                        },
                                        "finish_reason": None
                                    }
                                ]
                            }
                            yield f"data: {json.dumps(chunk)}\n\n"
                        else:
                            # Send final chunk
                            final_chunk = {
                                "id": "chatcmpl-agriculture-ai",
                                "object": "chat.completion.chunk",
                                "created": 1677610602,
                                "model": os.getenv("LLM_MODEL", "agriculture-ai-assistant"),
                                "choices": [
                                    {
                                        "index": 0,
                                        "delta": {},
                                        "finish_reason": "stop"
                                    }
                                ]
                            }
                            yield f"data: {json.dumps(final_chunk)}\n\n"
                            yield "data: [DONE]\n\n"
                except Exception as e:
                    logger.error(f"Error in OpenAI streaming: {e}")
                    error_chunk = {
                        "error": {
                            "message": str(e),
                            "type": "internal_error"
                        }
                    }
                    yield f"data: {json.dumps(error_chunk)}\n\n"
            
            return StreamingResponse(
                generate_openai_stream(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/plain; charset=utf-8"
                }
            )
        else:
            # Non-streaming response
            full_response = ""
            async for content_chunk, is_complete in chat_service.generate_streaming_response(request=chat_request):
                if not is_complete:
                    full_response += content_chunk
            
            return {
                "id": "chatcmpl-agriculture-ai",
                "object": "chat.completion",
                "created": 1677610602,
                "model": os.getenv("LLM_MODEL", "agriculture-ai-assistant"),
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": full_response
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(last_message.split()),
                    "completion_tokens": len(full_response.split()),
                    "total_tokens": len(last_message.split()) + len(full_response.split())
                }
            }
    except Exception as e:
        logger.error(f"Error in chat completions: {e}")
        return {
            "error": {
                "message": str(e),
                "type": "internal_error"
            }
        }

# Streamlit integration
@app.get("/streamlit")
async def redirect_to_streamlit():
    """Redirect to Streamlit app"""
    return {"message": "Streamlit app is running on port 8501", "url": "http://localhost:8501"}

# Note: Streamlit runs as a separate process
# You can start it with: streamlit run src/ui/streamlit_app.py --server.port 8501