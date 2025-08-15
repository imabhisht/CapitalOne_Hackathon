import streamlit as st
import requests
import json
import uuid
import time
from datetime import datetime
import re


# Configure Streamlit page
st.set_page_config(
    page_title="CapitalOne Agentic Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern Open WebUI-inspired CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* Header */
    .app-header {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .app-subtitle {
        color: rgba(255, 255, 255, 0.7);
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    /* Chat Container */
    .chat-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        min-height: 60vh;
        max-height: 70vh;
        overflow-y: auto;
    }
    
    /* Message Styles */
    .message-container {
        display: flex;
        margin-bottom: 1.5rem;
        animation: fadeIn 0.3s ease-in;
    }
    
    .user-message {
        justify-content: flex-end;
    }
    
    .assistant-message {
        justify-content: flex-start;
    }
    
    .message-bubble {
        max-width: 70%;
        padding: 1rem 1.5rem;
        border-radius: 18px;
        position: relative;
        word-wrap: break-word;
    }
    
    .user-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: auto;
    }
    
    .assistant-bubble {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: rgba(255, 255, 255, 0.9);
        margin-right: auto;
    }
    
    .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 0.75rem;
        font-size: 1.2rem;
        flex-shrink: 0;
    }
    
    .user-avatar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        order: 2;
    }
    
    .assistant-avatar {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        order: 1;
    }
    
    /* Input Area */
    .input-container {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1rem;
        position: sticky;
        bottom: 0;
        backdrop-filter: blur(10px);
    }
    
    /* Streamlit Input Styling */
    .stChatInput > div > div > div > div {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 25px !important;
        color: white !important;
    }
    
    .stChatInput > div > div > div > div > input {
        color: white !important;
        background: transparent !important;
        border: none !important;
        padding: 1rem 1.5rem !important;
        font-size: 1rem !important;
    }
    
    .stChatInput > div > div > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.03) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    
    .status-online {
        background: rgba(34, 197, 94, 0.2);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .status-offline {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .typing-indicator {
        animation: pulse 1.5s infinite;
    }
    
    /* Scrollbar */
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 3px;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 3px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.3);
    }
    
    /* Text styling */
    .stMarkdown {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    /* Select box styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize sidebar navigation and history
mode = st.sidebar.radio("Navigate", ["Chat", "History"], index=0, format_func=lambda x: "💬 Chat" if x=="Chat" else "📜 History")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if mode == "History":
    st.title("📜 Chat History")
    if not st.session_state.chat_history:
        st.info("No past chats yet.")
    else:
        for session in st.session_state.chat_history:
            cols = st.columns([4,1])
            cols[0].markdown(f"**Session:** {session['chat_session_id']}")
            if cols[1].button("Continue", key=f"cont_{session['chat_session_id']}"):
                st.session_state.messages = session["messages"]
                st.session_state.chat_session_id = session["chat_session_id"]
                st.experimental_rerun()
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = f"streamlit_user_{str(uuid.uuid4())[:8]}"
if "chat_session_id" not in st.session_state:
    st.session_state.chat_session_id = None

# Modern Header
st.markdown("""
<div class="app-header">
    <div class="app-title">😄 CapitalOne Agentic Assistant</div>
    <div class="app-subtitle">Your intelligent agricultural assistant powered by advanced AI</div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Chat Settings")
    
    # API Configuration
    with st.expander("🔧 API Configuration"):
        api_url = st.text_input(
            "Backend API URL",
            value="http://localhost:5050",
            help="URL of the FastAPI backend server"
        )
        
        # Test connection button
        if st.button("🔍 Test Connection"):
            try:
                response = requests.get(f"{api_url}/health", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Connection successful!")
                    health_data = response.json()
                    st.json(health_data)
                else:
                    st.error(f"❌ Connection failed: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection error: {e}")
    
    # Display session info
    st.info(f"**User ID:** {st.session_state.user_id}")
    if st.session_state.chat_session_id:
        st.info(f"**Session ID:** {st.session_state.chat_session_id}")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        # save current conversation to history
        if st.session_state.chat_session_id and st.session_state.messages:
            st.session_state.chat_history.append({
                "chat_session_id": st.session_state.chat_session_id,
                "messages": st.session_state.messages.copy()
            })
        # clear messages and session
        st.session_state.messages = []
        st.session_state.chat_session_id = None
        st.rerun()
    
    # Smart Routing Settings
    with st.expander("🧠 Smart Routing"):
        st.markdown("**Routing helps speed up responses by using a smaller, faster model for simple tasks.**")
        
        # Test routing for a message
        test_message = st.text_input("Test routing for message:", placeholder="Enter a message to see routing decision...")
        
        if test_message and st.button("🔍 Analyze Routing"):
            try:
                response = requests.post(
                    f"{api_url}/routing/analyze",
                    json={"message": test_message},
                    timeout=5
                )
                if response.status_code == 200:
                    routing_data = response.json()
                    routing_info = routing_data["routing_decision"]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Classification", routing_info["classification"])
                        st.metric("Confidence", f"{routing_info['confidence']:.2f}")
                    with col2:
                        st.metric("Selected Model", routing_info["selected_model"])
                        st.metric("Word Count", routing_info["word_count"])
                    
                    if routing_info["use_small_llm"]:
                        st.success("✅ Will use fast small model")
                    else:
                        st.info("🔄 Will use main model")
                else:
                    st.error(f"Routing analysis failed: {response.status_code}")
            except Exception as e:
                st.error(f"Error analyzing routing: {e}")
    
    # Language selection (for future use)
    language = st.selectbox(
        "Language",
        ["English", "Spanish", "French"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This AI assistant helps with agricultural queries, 
    crop management, weather analysis, and farming best practices.
    
    **Backend Status:** Make sure the FastAPI server is running on port 5050.
    """)

# Main chat interface
st.header("💬 Chat")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # start new session if needed
    if not st.session_state.chat_session_id:
        st.session_state.chat_session_id = f"session_{str(uuid.uuid4())[:8]}"
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        # Initialize variables
        thinking_content = ""
        main_response = ""
        full_response = ""
        has_thinking = False
        in_thinking = False
        thinking_placeholder = None
        main_placeholder = None
        
        # Helper: extract thinking and main response from streamed text (moved before usage)
        def extract_thinking_and_response(text):
            """Extract thinking content and main response from text."""
            # Look for <think>...</think> pattern
            think_pattern = r'<think>(.*?)</think>'
            think_match = re.search(think_pattern, text, re.DOTALL)
            
            if think_match:
                thinking = think_match.group(1).strip()
                # Remove the thinking part from the main response
                main_content = re.sub(think_pattern, '', text, flags=re.DOTALL).strip()
                return thinking, main_content, True
            else:
                # No thinking tags found, return entire response as main content
                return "", text.strip(), False

        try:
            # Use the API URL from sidebar (default to localhost:5050)
            API_BASE_URL = api_url if 'api_url' in locals() else "http://localhost:5050"
            
            # Create request payload
            request_data = {
                "message": prompt,
                "user_id": st.session_state.user_id,
                "session_id": st.session_state.chat_session_id
            }
            
            # Make API request to FastAPI backend
            try:
                response = requests.post(
                    f"{API_BASE_URL}/chat/stream",
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    stream=True,
                    timeout=30
                )
                
                if response.status_code == 200:
                    # Create containers for streaming display
                    thinking_expander = None
                    main_container = st.empty()
                    
                    # Process streaming response
                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode('utf-8')
                            if line_str.startswith('data: '):
                                try:
                                    data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                                    content = data.get('content', '')
                                    is_complete = data.get('is_complete', False)
                                    
                                    if not is_complete and content:
                                        full_response += content
                                        
                                        # Real-time parsing during streaming
                                        current_thinking, current_main, currently_has_thinking = extract_thinking_and_response(full_response)
                                        
                                        # Handle thinking content display
                                        if currently_has_thinking and current_thinking:
                                            if not has_thinking:  # First time we detect thinking
                                                has_thinking = True
                                                thinking_expander = st.expander("🤔 Thinking process", expanded=False)
                                                with thinking_expander:
                                                    thinking_placeholder = st.empty()
                                            
                                            # Update thinking content
                                            if thinking_placeholder:
                                                thinking_placeholder.markdown(f"*{current_thinking}*")
                                        
                                        # Handle main response display
                                        if current_main:
                                            if has_thinking:
                                                # Show main response below thinking expander
                                                main_container.markdown(current_main)
                                            else:
                                                # No thinking detected, show full response
                                                main_container.markdown(full_response + "▌")
                                        elif not has_thinking:
                                            # Still streaming, show cursor
                                            main_container.markdown(full_response + "▌")
                                    
                                    elif is_complete:
                                        break
                                        
                                except json.JSONDecodeError:
                                    continue
                    
                    # Final display after streaming is complete
                    final_thinking, final_main, final_has_thinking = extract_thinking_and_response(full_response)
                    
                    if final_has_thinking and final_thinking:
                        # Ensure thinking expander exists
                        if not thinking_expander:
                            thinking_expander = st.expander("🤔 Thinking process", expanded=False)
                            with thinking_expander:
                                st.markdown(f"*{final_thinking}*")
                        
                        # Show final main response
                        if final_main:
                            main_container.markdown(final_main)
                            # Store only the main response for chat history
                            response_for_history = final_main
                        else:
                            main_container.markdown("*No main response content*")
                            response_for_history = "*No main response content*"
                    else:
                        # No thinking content, show full response
                        if full_response:
                            main_container.markdown(full_response)
                            response_for_history = full_response
                        else:
                            main_container.markdown("*No response received*")
                            response_for_history = "*No response received*"
                    
                    # Set the response for chat history
                    full_response = response_for_history
                    
                    # Show routing info if available
                    try:
                        routing_response = requests.post(
                            f"{API_BASE_URL}/routing/analyze",
                            json={"message": prompt},
                            timeout=2
                        )
                        if routing_response.status_code == 200:
                            routing_data = routing_response.json()
                            routing_info = routing_data["routing_decision"]
                            
                            # model_used = "🚀 Small Model" if routing_info["use_small_llm"] else "🧠 Main Model"
                            # st.caption(f"*Processed with {model_used} (Classification: {routing_info['classification']}, Confidence: {routing_info['confidence']:.2f})*")
                    except:
                        pass  # Don't show routing info if it fails
                    
                else:
                    error_message = f"❌ API Error: {response.status_code} - {response.text}"
                    st.markdown(error_message)
                    full_response = error_message
                    
            except requests.exceptions.ConnectionError:
                error_message = "❌ **Connection Error:** Cannot connect to the backend API at http://localhost:5050. Please make sure the FastAPI server is running."
                st.markdown(error_message)
                st.error("💡 **Tip:** Run `python main.py` or `python app.py` in the backend directory to start the API server.")
                full_response = error_message
                
            except requests.exceptions.Timeout:
                error_message = "❌ **Timeout Error:** The request took too long to complete."
                st.markdown(error_message)
                full_response = error_message
                
            except Exception as api_error:
                error_message = f"❌ **API Error:** {str(api_error)}"
                st.markdown(error_message)
                full_response = error_message
            
        except Exception as e:
            error_message = f"❌ **Error:** {str(e)}"
            st.error(f"Chat error: {e}")
            st.markdown(error_message)
            full_response = error_message
   

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8em;">
    Powered by CapitalOne Agentic Assistant | Built with Streamlit
</div>
""", unsafe_allow_html=True)