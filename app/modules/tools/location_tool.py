"""
Location tool for getting user's browser location.
"""
from typing import Dict, Optional
from streamlit_local_storage import LocalStorage
from ...config import get_logger

# Initialize logger
logger = get_logger(__name__)

def get_browser_location() -> Optional[Dict]:
    logger.debug("Attempting to get browser location from localStorage")
    
    try:
        localS = LocalStorage()
        lat = localS.getItem("userLat")
        lon = localS.getItem("userLon")
        
        logger.debug(f"Retrieved from localStorage - lat: {lat}, lon: {lon}")
        
        if lat and lon:
            try:
                location_data = {
                    "lat": float(lat),
                    "lon": float(lon),
                    "source": "browser_geolocation_localstorage"
                }
                logger.info(f"Browser location available: {location_data['lat']}, {location_data['lon']}")
                return location_data
            except Exception as e:
                logger.error(f"Invalid coordinates in localStorage: {str(e)}")
                return {"error": "Invalid coordinates in localStorage"}
        else:
            logger.debug("No location data found in localStorage")
            return None
    except Exception as e:
        logger.error(f"Error accessing localStorage: {str(e)}")
        return {"error": f"Error accessing localStorage: {str(e)}"}

def tool_get_lat_lon_from_browser() -> Dict:
    logger.info("Tool called: get_lat_lon_from_browser")
    
    loc = get_browser_location()
    if loc and not loc.get("error"):
        logger.info("Browser location successfully retrieved")
        return {
            "success": True,
            "coordinates": {
                "lat": loc.get("lat"),
                "lon": loc.get("lon")
            },
            "accuracy_meters": loc.get("accuracy"),
            "timestamp": loc.get("timestamp"),
            "source": "browser_geolocation"
        }
    else:
        error_msg = loc.get("error") if loc else "Browser location not available"
        logger.warning(f"Browser location unavailable: {error_msg}")
        return {
            "success": False,
            "error": "Browser location not available. User may need to grant location permission or location services may be disabled.",
            "suggestion": "Please enable location services in your browser or provide coordinates manually."
        }