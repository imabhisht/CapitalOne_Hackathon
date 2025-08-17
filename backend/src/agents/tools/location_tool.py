from langchain_core.tools import tool
from typing import Dict, Any, Optional
import logging
import requests
import os

logger = logging.getLogger(__name__)

# Global variable to store current session context
_current_session_id = None

def set_session_context(session_id: str):
    """Set the current session ID for location tool context"""
    global _current_session_id
    _current_session_id = session_id

def get_session_context() -> Optional[str]:
    """Get the current session ID"""
    global _current_session_id
    return _current_session_id


@tool
def get_user_current_location() -> Dict[str, Any]:
    """
    Get the user's current location coordinates.
    
    Returns:
        Dict containing latitude and longitude coordinates, or error if not available
    """
    try:
        print("Fetching user location...")
        print('---------------------------')
        # Get user location from session
        session_id = get_session_context()
        
        if not session_id:
            return {
                "error": "No session context available",
                "source": "no_session"
            }
        
        try:
            # Try to import and use session storage
            from src.services.session_storage import session_storage
            location_data = session_storage.get_location_sync(session_id)
            
            if not location_data:
                return {
                    "error": "No location data found in session",
                    "session_id": session_id,
                    "source": "no_location_data"
                }
            
            latitude = location_data.get('latitude')
            longitude = location_data.get('longitude')
            
            if latitude is None or longitude is None:
                return {
                    "error": "Invalid location data in session",
                    "session_id": session_id,
                    "source": "invalid_location_data"
                }
            
            # Validate coordinate ranges
            if not (-90 <= latitude <= 90):
                return {
                    "error": f"Invalid latitude: {latitude}. Must be between -90 and 90",
                    "source": "invalid_coordinates"
                }
            
            if not (-180 <= longitude <= 180):
                return {
                    "error": f"Invalid longitude: {longitude}. Must be between -180 and 180",
                    "source": "invalid_coordinates"
                }
            
            # get the name of city
            # city_info = reverse_geocode_coordinates(latitude, longitude)
            print("111111")
            coordinates = {
                "latitude": latitude,
                "longitude": longitude,
                "session_id": session_id,
                # "city": city_info.get("city"),
                # "district": city_info.get("district"),
                # "state": city_info.get("state"),
                # "country": city_info.get("country"),
                "source": "user_session",
                "success": True
            }
            
            logger.info(f"Successfully retrieved user location from session {session_id}: ({latitude}, {longitude})")
            return coordinates
            
        except ImportError:
            logger.warning("Session storage module not available")
            return {
                "error": "Session storage service not available",
                "source": "service_unavailable"
            }
        except Exception as e:
            logger.error(f"Error retrieving location from session {session_id}: {e}")
            return {
                "error": f"Failed to retrieve location from session: {str(e)}",
                "session_id": session_id,
                "source": "session_error"
            }
        
    except Exception as e:
        logger.error(f"Error getting user location: {e}")
        return {
            "error": f"Failed to get user location: {str(e)}",
            "source": "location_service_error"
        }