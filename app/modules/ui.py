"""
UI helper functions for Streamlit app.
"""
import streamlit as st
import streamlit.components.v1 as components
from ..config import get_logger

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
    logger.debug(f"Streaming markdown response - Length: {len(text)} characters, Delay: {delay}s")
    
    import time
    container = st.empty()
    words = text.split()
    streamed = ""
    
    logger.debug(f"Response split into {len(words)} words for streaming")
    
    for i, word in enumerate(words):
        streamed += word + " "
        container.markdown(streamed + "▌")
        time.sleep(delay)
        
        # Log progress every 20 words to avoid spam
        if (i + 1) % 20 == 0:
            logger.debug(f"Streaming progress: {i + 1}/{len(words)} words")
    
    container.markdown(streamed)
    logger.debug("Markdown streaming completed")
