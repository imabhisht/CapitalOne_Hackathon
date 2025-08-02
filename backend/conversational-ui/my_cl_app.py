# ./conversational-ui/my_cl_app.py
import chainlit as cl
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import chat service
from chat_service import chat_service

@cl.set_chat_profiles
async def set_chat_profiles():
    return [
        cl.ChatProfile(
            name="Default",
            markdown_description="Welcome to the Capital One Hackathon Assistant!",
            icon="https://raw.githubusercontent.com/imabhisht/CapitalOne_Hackathon/refs/heads/master/backend/public/logo.png",
        )
    ]

@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session"""
    pass

@cl.on_message
async def handle_message(message: cl.Message):
    """Handle incoming messages"""
    
    # Parse provider from message if specified
    content = message.content.strip()
    provider = None
    
    if content.startswith('@'):
        parts = content.split(' ', 1)
        if len(parts) > 1:
            provider = parts[0][1:]  # Remove @ symbol
            content = parts[1]
            
            # Validate provider
            if provider not in chat_service.get_available_providers():
                await cl.Message(
                    content=f"❌ Provider '{provider}' not available. Available providers: {', '.join(chat_service.get_available_providers())}"
                ).send()
                return
    
    # Create response message
    msg = cl.Message(content="")
    await msg.send()
    
    try:
        accumulated_content = ""
        provider_used = provider or chat_service.default_provider
        
        # Add provider indicator
        if provider:
            msg.content = f"🔄 Using **{provider_used}** provider...\n\n"
            await msg.update()
            accumulated_content = f"🔄 Using **{provider_used}** provider...\n\n"
        
        # Stream response
        async for content_chunk, is_complete in chat_service.generate_streaming_response(
            content, 
            provider=provider
        ):
            if is_complete:
                break
            
            accumulated_content += content_chunk
            msg.content = accumulated_content
            await msg.update()
        
        # Add final provider info
        if not provider:
            final_content = accumulated_content + f"\n\n*Used provider: {provider_used}*"
            msg.content = final_content
            await msg.update()
    
    except Exception as e:
        msg.content = f"❌ **Error:** {str(e)}"
        await msg.update()

@cl.on_settings_update
async def setup_agent(settings):
    """Handle settings updates (if you want to add settings UI later)"""
    pass