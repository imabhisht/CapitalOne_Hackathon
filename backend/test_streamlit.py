#!/usr/bin/env python3
"""
Simple test Streamlit app to debug chat functionality
"""
import streamlit as st
import sys
import os
import uuid

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

st.set_page_config(page_title="Chat Test", page_icon="🧪")

st.title("🧪 Chat Service Test")

# Test imports
try:
    from services.chat_service import chat_service
    from models.chat_request import ChatRequest
    st.success("✅ Successfully imported chat service and models")
except Exception as e:
    st.error(f"❌ Import error: {e}")
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = f"test_user_{str(uuid.uuid4())[:8]}"

st.info(f"User ID: {st.session_state.user_id}")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Test message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Test response
    with st.chat_message("assistant"):
        try:
            # Simple test without streaming
            request = ChatRequest(
                message=prompt,
                user_id=st.session_state.user_id
            )
            
            st.write("✅ ChatRequest created successfully")
            st.write(f"Request: {request}")
            
            # Try to call the service
            response = "Test response: I received your message!"
            st.markdown(response)
            
            # Add to history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})