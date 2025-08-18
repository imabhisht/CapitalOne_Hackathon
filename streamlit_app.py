
# --- Modular Imports ---
import streamlit as st
from dotenv import load_dotenv
from app.modules.tools import get_browser_location
from app.modules.api import openrouter_tools_schema, call_openrouter_chat, handle_tool_calls
from app.modules.prompts import generate_system_prompt
from app.modules.ui import add_location_permission, request_location_with_retry, stream_markdown_response
from app.config import setup_logging, get_logger, APP_NAME, VERSION
import os

# Load env variables from .env if present
load_dotenv(override=False)

# Setup logging
log_file = setup_logging()
logger = get_logger(__name__)

APP_TITLE = "Smart Location-Aware Assistant"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")

# Log application startup
logger.info(f"Starting {APP_NAME} v{VERSION}")
logger.info(f"Log file: {log_file}")
logger.info(f"OpenRouter Model: {OPENROUTER_MODEL}")
logger.info(f"API Keys configured - OpenRouter: {'Yes' if OPENROUTER_API_KEY else 'No'}, Weather: {'Yes' if WEATHERAPI_KEY else 'No'}")

st.set_page_config(
    page_title=APP_TITLE, 
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

logger.debug("Streamlit page configuration set")

add_location_permission()
logger.debug("Location permission component added")

if not get_browser_location():
    logger.info("Browser location not available, requesting location")
    request_location_with_retry()
else:
    logger.debug("Browser location is available")

st.title(APP_TITLE)
st.markdown("*Your intelligent location-aware assistant with real-time weather and contextual information*")

with st.sidebar:
    st.markdown("### 🚀 Quick Start")
    st.markdown("""
    1. **Enable Location**: Click 'Request Location' to share your coordinates
    2. **Ask Questions**: Try queries like:
       - "What's the weather like here?"
       - "Should I bring a jacket?"
       - "What's the weather in Tokyo?"
    3. **Get Contextual Answers**: Receive location-aware responses
    """)
    st.divider()
    st.markdown("### ⚙️ Configuration")
    config_status = {
        "OpenRouter API": "✅ Connected" if OPENROUTER_API_KEY else "❌ Missing Key",
        "Weather API": "✅ Connected" if WEATHERAPI_KEY else "❌ Missing Key",
        "Model": OPENROUTER_MODEL,
        "Endpoint": OPENROUTER_API_BASE
    }
    for key, status in config_status.items():
        st.markdown(f"**{key}**: {status}")
    if not OPENROUTER_API_KEY or not WEATHERAPI_KEY:
        st.warning("⚠️ Some features may be limited without API keys. Check your .env file.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    logger.debug("Initialized empty chat history")
else:
    logger.debug(f"Chat history exists with {len(st.session_state.messages)} messages")

# Display current location status
location_data = get_browser_location()
if location_data:
    if location_data.get("error"):
        logger.warning(f"Location error: {location_data['error']}")
        st.error(f"Location Error: {location_data['error']}")
        st.info("You can still use the assistant by providing location names manually.")
    else:
        lat, lon = location_data.get('lat'), location_data.get('lon')
        accuracy = location_data.get('accuracy', 0)
        logger.info(f"User location available: {lat:.4f}, {lon:.4f} (accuracy: {int(accuracy)}m)")
        st.success(f"Current Location: {lat:.4f}, {lon:.4f} (accuracy: {int(accuracy)}m)")
else:
    logger.debug("No location data available")

st.markdown("### Chat")
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask me anything about weather, location, or get contextual advice..."):
    logger.info(f"User prompt received: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    
    user_msg = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_msg)
    with st.chat_message("user"):
        st.markdown(prompt)
    
    logger.debug("Generating system prompt...")
    system_prompt = generate_system_prompt(location_data)
    logger.debug("Getting tool schemas...")
    tools = openrouter_tools_schema()
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking and gathering information..."):
            try:
                logger.info("Making initial OpenRouter API call...")
                response = call_openrouter_chat(
                    st.session_state.messages,
                    system_prompt,
                    tools=tools,
                    tool_choice="auto"
                )
                
                if response.get("error"):
                    logger.error(f"OpenRouter API error: {response['error']}")
                    final_response = f"Error: {response['error']}"
                else:
                    logger.debug("Initial API call successful, processing response...")
                    choice = response.get("choices", [{}])[0]
                    tool_messages = handle_tool_calls(choice)
                    
                    if tool_messages:
                        logger.info(f"Tool calls detected: {len(tool_messages)} tools to execute")
                    
                    max_iterations = 5
                    iteration = 0
                    while tool_messages and iteration < max_iterations:
                        iteration += 1
                        logger.debug(f"Tool execution iteration {iteration}/{max_iterations}")
                        
                        assistant_msg = choice.get("message", {}).copy()
                        assistant_msg = {k: v for k, v in assistant_msg.items() if v is not None}
                        full_conversation = st.session_state.messages + [assistant_msg] + tool_messages
                        
                        tool_name = tool_messages[0]["name"] if tool_messages and tool_messages[0].get("name") else "tool"
                        logger.info(f"Executing tool: {tool_name}")
                        
                        with st.spinner(f"Calling {tool_name}... (attempt {iteration})"):
                            follow_up = call_openrouter_chat(
                                full_conversation,
                                system_prompt,
                                tools=tools,
                                tool_choice="auto"
                            )
                        
                        if follow_up.get("error"):
                            logger.error(f"Follow-up API call error: {follow_up['error']}")
                            final_response = f"Follow-up error: {follow_up['error']}"
                            break
                        else:
                            choice = follow_up.get("choices", [{}])[0]
                            new_tool_messages = handle_tool_calls(choice)
                            
                            if new_tool_messages == tool_messages:
                                logger.debug("No new tool calls, breaking loop")
                                break
                            
                            tool_messages = new_tool_messages
                            if not tool_messages:
                                final_response = choice.get("message", {}).get("content", "No response generated.")
                                logger.debug("No more tool calls needed, got final response")
                                break
                    
                    if iteration >= max_iterations:
                        logger.warning(f"Reached maximum iterations ({max_iterations}), forcing final response")
                        msg = st.session_state.messages + [assistant_msg] + tool_messages
                        final_ai_response = call_openrouter_chat(
                            msg,
                            system_prompt,
                            tools=tools,
                            tool_choice=None,
                            temperature=0.5,
                            max_tokens=500
                        )
                        final_response = final_ai_response.get("choices", [{}])[0].get("message", {}).get("content", "No response generated.")
                    
                    if iteration == 0:
                        final_response = choice.get("message", {}).get("content", "No response generated.")
                        logger.debug("No tool calls were made, using direct response")
                        
            except Exception as e:
                logger.error(f"Unexpected error during chat processing: {str(e)}", exc_info=True)
                final_response = f"Unexpected error: {str(e)}"
                import traceback
                print(f"Full traceback: {traceback.format_exc()}")
        
        logger.info(f"Final response length: {len(final_response) if final_response else 0} characters")
        
        if final_response and len(final_response) > 80:
            logger.debug("Streaming response to user")
            stream_markdown_response(final_response)
        else:
            logger.debug("Displaying response directly")
            st.markdown(final_response)
            
        st.session_state.messages.append({"role": "assistant", "content": final_response})
        logger.debug("Response added to chat history")

st.markdown("---")
st.markdown("### Tips for Better Results")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    **Weather Queries**
    - "What's the weather here?"
    - "Should I bring an umbrella?"
    - "Weather in Tokyo"
    """)
with col2:
    st.markdown("""
    **Location Context**
    - "Best restaurants nearby"
    - "Local time zone"
    - "Activities for this weather"
    """)
with col3:
    st.markdown("""
    **Setup**
    - Add API keys to .env file
    - Enable browser location
    - Try specific coordinates
    """)
st.caption("Your location data is only used for this session and is not stored permanently.")