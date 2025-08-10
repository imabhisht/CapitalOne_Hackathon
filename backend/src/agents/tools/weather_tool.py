"""
Weather tool for getting weather information.
"""

from langchain_core.tools import tool
from typing import Dict, Any
import logging
import random

logger = logging.getLogger(__name__)

@tool
def get_weather(location: str = "Baroda, Jamjodhpur") -> Dict[str, Any]:
    """
    Get weather information for a location.
    
    Args:
        location: Location to get weather for
        
    Returns:
        Dict containing weather information
    """
    try:
        # Mock weather data
        weather_data = {
            "location": location,
            "temperature": {
                "current": random.randint(25, 35),
                "feels_like": random.randint(27, 38),
                "min": random.randint(20, 25),
                "max": random.randint(35, 42)
            },
            "humidity": random.randint(40, 80),
            "wind_speed": random.randint(5, 20),
            "conditions": random.choice(["Sunny", "Partly Cloudy", "Cloudy", "Light Rain"]),
            "visibility": "10 km",
            "uv_index": random.randint(3, 8),
            "forecast": [
                {
                    "day": "Today",
                    "high": random.randint(35, 42),
                    "low": random.randint(20, 25),
                    "condition": "Sunny"
                },
                {
                    "day": "Tomorrow", 
                    "high": random.randint(33, 40),
                    "low": random.randint(22, 27),
                    "condition": "Partly Cloudy"
                }
            ]
        }
        
        logger.info(f"Retrieved weather data for: {location}")
        return weather_data
        
    except Exception as e:
        logger.error(f"Error getting weather data: {e}")
        return {
            "error": f"Failed to get weather data: {str(e)}",
            "location": location
        }