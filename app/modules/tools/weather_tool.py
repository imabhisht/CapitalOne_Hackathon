"""
Weather tool for getting weather information by coordinates.
"""
import os
import requests
from typing import Dict
from ...config import get_logger

# Initialize logger
logger = get_logger(__name__)

WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")

def tool_get_weather_by_coords(lat: float, lon: float) -> Dict:
    logger.info(f"Getting weather data for coordinates: {lat}, {lon}")
    
    if not WEATHERAPI_KEY:
        logger.error("WEATHERAPI_KEY is not set in environment variables")
        return {"error": "WEATHERAPI_KEY is not set in environment variables"}
    
    try:
        url = "https://api.weatherapi.com/v1/current.json"
        params = {"key": WEATHERAPI_KEY, "q": f"{lat},{lon}", "aqi": "yes"}
        
        logger.debug(f"Making request to WeatherAPI: {url}")
        logger.debug(f"Request parameters: {params}")
        
        r = requests.get(url, params=params, timeout=10)
        
        logger.debug(f"WeatherAPI response status: {r.status_code}")
        
        if r.status_code >= 400:
            logger.error(f"WeatherAPI error {r.status_code}: {r.text}")
            return {"error": f"WeatherAPI error {r.status_code}", "details": r.text}
        
        data = r.json()
        logger.debug("WeatherAPI response received successfully")
        
        # Extract location name for logging
        location_name = data.get("location", {}).get("name", "Unknown")
        country = data.get("location", {}).get("country", "Unknown")
        logger.info(f"Weather data retrieved for: {location_name}, {country}")
        
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
        
        if data.get("current", {}).get("air_quality"):
            weather_info["air_quality"] = data.get("current", {}).get("air_quality")
            logger.debug("Air quality data included in response")
        
        logger.info("Weather data successfully formatted and ready to return")
        return weather_info
        
    except requests.RequestException as e:
        logger.error(f"Network error calling WeatherAPI: {str(e)}")
        return {"error": f"Network error calling WeatherAPI: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error calling WeatherAPI: {str(e)}", exc_info=True)
        return {"error": f"Unexpected error calling WeatherAPI: {str(e)}"}