from fastapi import FastAPI
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from chainlit.utils import mount_chainlit
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json

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

class ChatResponse(BaseModel):
    content: str
    is_complete: bool = False

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")

@app.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """Stream response using the chat service"""
    
    async def generate_stream():
        async for content_chunk, is_complete in chat_service.generate_streaming_response(request.message):
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

# Mount Chainlit
mount_chainlit(app=app, target="./conversational-ui/my_cl_app.py", path="/chat")