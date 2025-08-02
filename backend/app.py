# app.py
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from chainlit.utils import mount_chainlit

from pydantic import BaseModel
import json
import os

# Import our chat service
from chat_service import chat_service, generate_streaming_response



app = FastAPI(title="Streaming Chat API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    provider: str = None  # Optional provider selection

class ChatResponse(BaseModel):
    content: str
    is_complete: bool = False

@app.get("/")
async def root():
    return {
        "message": "Streaming Chat API is running",
        "available_providers": chat_service.get_available_providers()
    }

@app.get("/providers")
async def get_providers():
    """Get available chat providers"""
    return {
        "providers": chat_service.get_available_providers(),
        "default": chat_service.default_provider
    }

@app.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """Stream response using the chat service"""
    
    async def generate_stream():
        async for content_chunk, is_complete in chat_service.generate_streaming_response(
            request.message, 
            provider=request.provider
        ):
            # Create response chunk
            chunk = {
                "content": content_chunk,
                "is_complete": is_complete
            }
            
            # Send the chunk as JSON
            yield f"data: {json.dumps(chunk)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )

@app.post("/chat")
async def chat_complete(request: ChatRequest):
    """Non-streaming endpoint"""
    response = await chat_service.generate_complete_response(
        request.message,
        provider=request.provider
    )
    return ChatResponse(content=response, is_complete=True)

# Initialize providers based on environment variables
def setup_providers():
    """Setup providers based on configuration"""
    
    # OpenAI setup
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        from chat_service import OpenAIChatProvider
        chat_service.add_provider("openai", OpenAIChatProvider(
            api_key=openai_key,
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        ))
        print("✅ OpenAI provider configured")
    
    # Anthropic setup
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        from chat_service import AnthropicChatProvider
        chat_service.add_provider("anthropic", AnthropicChatProvider(
            api_key=anthropic_key,
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        ))
        print("✅ Anthropic provider configured")
    
    # RAG setup
    if os.getenv("ENABLE_RAG", "false").lower() == "true":
        from chat_service import RAGChatProvider
        chat_service.add_provider("rag", RAGChatProvider())
        print("✅ RAG provider configured")
    
    # Set default provider
    default_provider = os.getenv("DEFAULT_PROVIDER", "static")
    if default_provider in chat_service.get_available_providers():
        chat_service.set_default_provider(default_provider)
        print(f"✅ Default provider set to: {default_provider}")

# Setup providers on startup
setup_providers()

# Mount Chainlit
mount_chainlit(app=app, target="./conversational-ui/my_cl_app.py", path="/chat")
