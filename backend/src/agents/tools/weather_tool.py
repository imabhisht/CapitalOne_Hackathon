"""
Weather tool for getting weather information.
"""

from langchain_core.tools import tool
from typing import Dict, Any
import logging
import random
import requests
import os

logger = logging.getLogger(__name__)

@tool
def get_weather(lat: float, lon: float) -> Dict:
    """Fetch current weather from WeatherAPI by coordinates.
    Returns a comprehensive JSON dict with weather information.

    Args:
        lat: Latitude of the location
        lon: Longitude of the location

    """
    WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")
    if not WEATHERAPI_KEY:
        return {"error": "WEATHERAPI_KEY is not set in environment variables"}
    
    try:
        url = "https://api.weatherapi.com/v1/current.json"
        params = {"key": WEATHERAPI_KEY, "q": f"{lat},{lon}", "aqi": "yes"}
        r = requests.get(url, params=params, timeout=10)
        
        if r.status_code >= 400:
            return {"error": f"WeatherAPI error {r.status_code}", "details": r.text}
        
        data = r.json()
        
        # Enhanced weather data with more useful information
        weather_info = {
            "location": {
                "name": data.get("location", {}).get("name"),
                "region": data.get("location", {}).get("region"),
                "country": data.get("location", {}).get("country"),
                "coordinates": {
                    "lat": data.get("location", {}).get("lat"),
                    "lon": data.get("location", {}).get("lon")
                },
                "timezone": data.get("location", {}).get("tz_id"),
                "local_time": data.get("location", {}).get("localtime"),
            },
            "current_weather": {
                "temperature": {
                    "celsius": data.get("current", {}).get("temp_c"),
                    "fahrenheit": data.get("current", {}).get("temp_f"),
                    "feels_like_c": data.get("current", {}).get("feelslike_c"),
                    "feels_like_f": data.get("current", {}).get("feelslike_f"),
                },
                "condition": {
                    "text": data.get("current", {}).get("condition", {}).get("text"),
                    "icon": data.get("current", {}).get("condition", {}).get("icon"),
                },
                "wind": {
                    "speed_kph": data.get("current", {}).get("wind_kph"),
                    "speed_mph": data.get("current", {}).get("wind_mph"),
                    "direction": data.get("current", {}).get("wind_dir"),
                    "degree": data.get("current", {}).get("wind_degree"),
                },
                "atmospheric": {
                    "humidity": data.get("current", {}).get("humidity"),
                    "pressure_mb": data.get("current", {}).get("pressure_mb"),
                    "visibility_km": data.get("current", {}).get("vis_km"),
                    "uv_index": data.get("current", {}).get("uv"),
                },
                "last_updated": data.get("current", {}).get("last_updated"),
            }
        }
        
        # Add air quality if available
        if data.get("current", {}).get("air_quality"):
            weather_info["air_quality"] = data.get("current", {}).get("air_quality")
        
        return weather_info
        
    except requests.RequestException as e:
        return {"error": f"Network error calling WeatherAPI: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error calling WeatherAPI: {str(e)}"}
