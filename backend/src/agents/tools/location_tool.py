"""
Location tool for getting location information.
"""

from langchain_core.tools import tool
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

@tool
def get_location(query: str = "") -> Dict[str, Any]:
    """
    Get location information. For now returns static location data for Baroda, Jamjodhpur.
    
    Args:
        query: Optional query string for location (currently ignored)
        
    Returns:
        Dict containing location information
    """
    try:
        # Static location data for Baroda, Jamjodhpur
        location_data = {
            "city": "Baroda",
            "district": "Jamjodhpur", 
            "state": "Gujarat",
            "country": "India",
            "coordinates": {
                "latitude": 22.3072,
                "longitude": 73.1812
            },
            "timezone": "Asia/Kolkata",
            "population": "Approximately 1.8 million",
            "area": "235 sq km",
            "elevation": "39 meters above sea level",
            "climate": "Semi-arid",
            "major_industries": ["Petrochemicals", "Pharmaceuticals", "Engineering", "Textiles"],
            "landmarks": ["Laxmi Vilas Palace", "Sayaji Baug", "EME Temple", "Baroda Museum"]
        }
        
        logger.info(f"Retrieved location data for query: {query}")
        return location_data
        
    except Exception as e:
        logger.error(f"Error getting location data: {e}")
        return {
            "error": f"Failed to get location data: {str(e)}",
            "city": "Unknown",
            "district": "Unknown"
        }