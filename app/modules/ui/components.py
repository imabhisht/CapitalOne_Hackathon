"""
UI helper functions for Streamlit app.
"""
import streamlit as st
import streamlit.components.v1 as components
from ...config import get_logger

# Initialize logger
logger = get_logger(__name__)

def add_location_permission():
    logger.debug("Adding location permission component to page")
    
    location_html = """
    <script>
    if (!window.locationRequested) {
        window.locationRequested = true;
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    localStorage.setItem('userLat', position.coords.latitude);
                    localStorage.setItem('userLon', position.coords.longitude);
                    console.log('Location stored:', position.coords.latitude, position.coords.longitude);
                },
                function(error) {
                    console.warn('Location permission denied:', error.message);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000
                }
            );
        }
    }
    </script>
    """
    components.html(location_html, height=0)
    logger.debug("Location permission component rendered")

def request_location_with_retry():
    logger.info("Requesting location with retry mechanism")
    
    components.html("""
    <script>
    function requestLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    localStorage.setItem('userLat', position.coords.latitude);
                    localStorage.setItem('userLon', position.coords.longitude);
                    console.log('Location stored successfully');
                },
                function(error) {
                    if (error.code === error.PERMISSION_DENIED) {
                        alert('Location blocked. For the best performance, please enable location access: Click the location icon in the address bar or go to browser Settings > Privacy > Location.');
                    }
                },
                { enableHighAccuracy: true, timeout: 10000 }
            );
        }
    }
    if (!window.locationAttempted) {
        window.locationAttempted = true;
        requestLocation();
    }
    window.requestLocationAgain = requestLocation;
    </script>
    """, height=0)
    
    logger.debug("Location retry component rendered")

def stream_markdown_response(text, delay=0.015):
    """
    Stream and render markdown response properly in Streamlit.
    
    Args:
        text (str): Markdown text to stream
        delay (float): Delay between characters in seconds
    """
    logger.debug(f"Streaming markdown response - Length: {len(text)} characters, Delay: {delay}s")
    
    import time
    import re
    
    container = st.empty()
    
    # If the text is short, just display it directly
    if len(text) < 80:
        container.markdown(text)
        logger.debug("Short text displayed directly")
        return
    
    # For longer texts, stream character by character for better markdown handling
    streamed = ""
    
    # Process the text to handle markdown properly
    # We'll stream character by character but be smart about markdown elements
    i = 0
    while i < len(text):
        char = text[i]
        streamed += char
        container.markdown(streamed + "▌")
        time.sleep(delay)
        i += 1
        
        # Log progress every 50 characters to avoid spam
        if i % 50 == 0:
            logger.debug(f"Streaming progress: {i}/{len(text)} characters")
    
    # Final render without cursor
    container.markdown(streamed)
    logger.debug("Markdown streaming completed")

def render_markdown_response(text):
    """
    Render markdown response properly in Streamlit without streaming.
    
    Args:
        text (str): Markdown text to render
    """
    logger.debug(f"Rendering markdown response - Length: {len(text)} characters")
    
    # Use Streamlit's markdown function which properly handles all markdown syntax
    st.markdown(text)
    logger.debug("Markdown rendering completed")
