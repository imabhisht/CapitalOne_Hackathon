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

@cl.on_chat_start
async def start():
    """Initialize chat session"""
    # Generate a unique user ID for this session
    import uuid
    user_id = f"chainlit_user_{str(uuid.uuid4())[:8]}"
    cl.user_session.set("user_id", user_id)
    # Session ID will be set after first message

@cl.on_message
async def handle_message(message: cl.Message):
    """Handle incoming messages"""
    
    # Get message content
    content = message.content.strip()
    
    # Get or create session ID for this user session
    session_id = cl.user_session.get("chat_session_id")
    user_id = cl.user_session.get("user_id", "chainlit_user")
    
    # Create response message
    msg = cl.Message(content="")
    await msg.send()
    
    try:
        accumulated_content = ""
        
        # Create a ChatRequest object
        request = ChatRequest(
            message=content,
            user_id=user_id,
            session_id=session_id,  # Use existing session or None for new session
            language_type="en"
        )
        
        # Stream response
        async for content_chunk, is_complete in chat_service.generate_streaming_response(request=request):
            if is_complete:
                break
            
            accumulated_content += content_chunk
            msg.content = accumulated_content
            await msg.update()
        
        # After first message, store the session ID for future messages
        if not session_id:
            current_session_id = chat_service.get_current_session_id()
            if current_session_id:
                cl.user_session.set("chat_session_id", current_session_id)
                print(f"🔗 Stored session ID for future messages: {current_session_id}")
        else:
            print(f"🔄 Using existing session ID: {session_id}")
    
    except Exception as e:
        msg.content = f"❌ **Error:** {str(e)}"
        await msg.update()

@cl.on_settings_update
async def setup_agent(settings):
    """Handle settings updates (if you want to add settings UI later)"""
    pass