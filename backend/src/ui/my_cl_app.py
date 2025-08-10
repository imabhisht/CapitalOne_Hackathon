import chainlit as cl
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__))))

# Import chat service
from services.chat_service import chat_service
from models.chat_request import ChatRequest

@cl.set_chat_profiles
async def set_chat_profiles():
    return [
        cl.ChatProfile(
            name="Default",
            icon="https://raw.githubusercontent.com/imabhisht/CapitalOne_Hackathon/refs/heads/master/backend/public/logo.png",
            markdown_description="""### Welcome To CapitalOne Agentic Assistant!"""
        )
    ]

@cl.on_message
async def handle_message(message: cl.Message):
    """Handle incoming messages"""
    
    # Get message content
    content = message.content.strip()
    
    # Create response message
    msg = cl.Message(content="")
    await msg.send()
    
    try:
        accumulated_content = ""
        
        # Create a ChatRequest object
        request = ChatRequest(
            message=content,
            user_id="chainlit_user",  # You can make this dynamic based on user session
            session_id=None,  # Let the service create a new session
            language_type="en"
        )
        
        # Stream response
        async for content_chunk, is_complete in chat_service.generate_streaming_response(request=request):
            if is_complete:
                break
            
            accumulated_content += content_chunk
            msg.content = accumulated_content
            await msg.update()
    
    except Exception as e:
        msg.content = f"❌ **Error:** {str(e)}"
        await msg.update()

@cl.on_settings_update
async def setup_agent(settings):
    """Handle settings updates (if you want to add settings UI later)"""
    pass