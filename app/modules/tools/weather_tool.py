"""
Weather tool for comprehensive weather information using WeatherAPI.com

This module provides access to:
- Current weather conditions
- Weather forecasts (up to 14 days)
- Weather alerts and warnings
- Historical weather data
- Air quality information

Functions:
- tool_get_weather_by_coords: Get current weather by coordinates
- tool_get_weather_forecast: Get weather forecast by coordinates
- tool_get_weather_forecast_by_location: Get weather forecast by location name
- tool_get_weather_alerts: Get weather alerts for a location
- tool_get_historical_weather: Get historical weather data

Requires WEATHERAPI_KEY environment variable to be set.
"""
import os
import requests
from typing import Dict
from ...config import get_logger
import dotenv

dotenv.load_dotenv()

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


def tool_get_weather_forecast(lat: float, lon: float, days: int = 3, alerts: bool = True, aqi: bool = True) -> Dict:
    """
    Get weather forecast for the specified coordinates.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        days (int): Number of forecast days (1-14, default 3)
        alerts (bool): Include weather alerts (default True)
        aqi (bool): Include air quality data (default True)
    
    Returns:
        Dict: Weather forecast data including daily and hourly forecasts
    """
    logger.info(f"Getting weather forecast for coordinates: {lat}, {lon} for {days} days")
    
    if not WEATHERAPI_KEY:
        logger.error("WEATHERAPI_KEY is not set in environment variables")
        return {"error": "WEATHERAPI_KEY is not set in environment variables"}
    
    # Validate days parameter
    if days < 1 or days > 14:
        logger.error(f"Invalid days parameter: {days}. Must be between 1 and 14")
        return {"error": "Days parameter must be between 1 and 14"}
    
    try:
        url = "https://api.weatherapi.com/v1/forecast.json"
        params = {
            "key": WEATHERAPI_KEY,
            "q": f"{lat},{lon}",
            "days": days,
            "alerts": "yes" if alerts else "no",
            "aqi": "yes" if aqi else "no"
        }
        
        logger.debug(f"Making request to WeatherAPI forecast: {url}")
        logger.debug(f"Request parameters: {params}")
        
        r = requests.get(url, params=params, timeout=15)
        
        logger.debug(f"WeatherAPI forecast response status: {r.status_code}")
        
        if r.status_code >= 400:
            logger.error(f"WeatherAPI forecast error {r.status_code}: {r.text}")
            return {"error": f"WeatherAPI forecast error {r.status_code}", "details": r.text}
        
        data = r.json()
        logger.debug("WeatherAPI forecast response received successfully")
        
        # Use the helper function to format the response
        return _format_forecast_response(data, aqi, alerts)
        
    except requests.RequestException as e:
        logger.error(f"Network error calling WeatherAPI forecast: {str(e)}")
        return {"error": f"Network error calling WeatherAPI forecast: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error calling WeatherAPI forecast: {str(e)}", exc_info=True)
        return {"error": f"Unexpected error calling WeatherAPI forecast: {str(e)}"}


def tool_get_weather_forecast_by_location(location: str, days: int = 3, alerts: bool = True, aqi: bool = True) -> Dict:
    """
    Get weather forecast for the specified location (city name, zipcode, etc.).
    
    Args:
        location (str): Location query (city name, zipcode, coordinates, etc.)
        days (int): Number of forecast days (1-14, default 3)
        alerts (bool): Include weather alerts (default True)
        aqi (bool): Include air quality data (default True)
    
    Returns:
        Dict: Weather forecast data including daily and hourly forecasts
    """
    logger.info(f"Getting weather forecast for location: {location} for {days} days")
    
    if not WEATHERAPI_KEY:
        logger.error("WEATHERAPI_KEY is not set in environment variables")
        return {"error": "WEATHERAPI_KEY is not set in environment variables"}
    
    # Validate days parameter
    if days < 1 or days > 14:
        logger.error(f"Invalid days parameter: {days}. Must be between 1 and 14")
        return {"error": "Days parameter must be between 1 and 14"}
    
    try:
        url = "https://api.weatherapi.com/v1/forecast.json"
        params = {
            "key": WEATHERAPI_KEY,
            "q": location,
            "days": days,
            "alerts": "yes" if alerts else "no",
            "aqi": "yes" if aqi else "no"
        }
        
        logger.debug(f"Making request to WeatherAPI forecast: {url}")
        logger.debug(f"Request parameters: {params}")
        
        r = requests.get(url, params=params, timeout=15)
        
        logger.debug(f"WeatherAPI forecast response status: {r.status_code}")
        
        if r.status_code >= 400:
            logger.error(f"WeatherAPI forecast error {r.status_code}: {r.text}")
            return {"error": f"WeatherAPI forecast error {r.status_code}", "details": r.text}
        
        data = r.json()
        
        # Use the same formatting logic as the coordinate-based function
        return _format_forecast_response(data, aqi, alerts)
        
    except requests.RequestException as e:
        logger.error(f"Network error calling WeatherAPI forecast: {str(e)}")
        return {"error": f"Network error calling WeatherAPI forecast: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error calling WeatherAPI forecast: {str(e)}", exc_info=True)
        return {"error": f"Unexpected error calling WeatherAPI forecast: {str(e)}"}


def tool_get_weather_alerts(location: str) -> Dict:
    """
    Get weather alerts for the specified location.
    
    Args:
        location (str): Location query (city name, zipcode, coordinates, etc.)
    
    Returns:
        Dict: Weather alerts data
    """
    logger.info(f"Getting weather alerts for location: {location}")
    
    if not WEATHERAPI_KEY:
        logger.error("WEATHERAPI_KEY is not set in environment variables")
        return {"error": "WEATHERAPI_KEY is not set in environment variables"}
    
    try:
        url = "https://api.weatherapi.com/v1/alerts.json"
        params = {
            "key": WEATHERAPI_KEY,
            "q": location
        }
        
        logger.debug(f"Making request to WeatherAPI alerts: {url}")
        logger.debug(f"Request parameters: {params}")
        
        r = requests.get(url, params=params, timeout=10)
        
        logger.debug(f"WeatherAPI alerts response status: {r.status_code}")
        
        if r.status_code >= 400:
            logger.error(f"WeatherAPI alerts error {r.status_code}: {r.text}")
            return {"error": f"WeatherAPI alerts error {r.status_code}", "details": r.text}
        
        data = r.json()
        logger.debug("WeatherAPI alerts response received successfully")
        
        # Extract location name for logging
        location_name = data.get("location", {}).get("name", "Unknown")
        country = data.get("location", {}).get("country", "Unknown")
        logger.info(f"Weather alerts retrieved for: {location_name}, {country}")
        
        alerts_info = {
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
            "alerts": {
                "alert_count": len(data.get("alerts", {}).get("alert", [])),
                "alerts": []
            }
        }
        
        # Process alerts
        alerts_data = data.get("alerts", {}).get("alert", [])
        for alert in alerts_data:
            alert_info = {
                "headline": alert.get("headline"),
                "message_type": alert.get("msgtype"),
                "severity": alert.get("severity"),
                "urgency": alert.get("urgency"),
                "areas": alert.get("areas"),
                "category": alert.get("category"),
                "certainty": alert.get("certainty"),
                "event": alert.get("event"),
                "note": alert.get("note"),
                "effective": alert.get("effective"),
                "expires": alert.get("expires"),
                "description": alert.get("desc"),
                "instruction": alert.get("instruction")
            }
            alerts_info["alerts"]["alerts"].append(alert_info)
        
        logger.info(f"Weather alerts data successfully formatted: {len(alerts_data)} alerts")
        return alerts_info
        
    except requests.RequestException as e:
        logger.error(f"Network error calling WeatherAPI alerts: {str(e)}")
        return {"error": f"Network error calling WeatherAPI alerts: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error calling WeatherAPI alerts: {str(e)}", exc_info=True)
        return {"error": f"Unexpected error calling WeatherAPI alerts: {str(e)}"}


def _format_forecast_response(data: Dict, aqi: bool = True, alerts: bool = True) -> Dict:
    """
    Helper function to format forecast response data consistently.
    
    Args:
        data (Dict): Raw API response data
        aqi (bool): Whether air quality data was requested
        alerts (bool): Whether alerts data was requested
    
    Returns:
        Dict: Formatted forecast data
    """
    logger.debug("Formatting forecast response data")
    
    # Extract location name for logging
    location_name = data.get("location", {}).get("name", "Unknown")
    country = data.get("location", {}).get("country", "Unknown")
    logger.info(f"Formatting weather forecast data for: {location_name}, {country}")
    
    # Format the forecast response
    forecast_info = {
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
                "code": data.get("current", {}).get("condition", {}).get("code"),
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
        },
        "forecast": {
            "days": []
        }
    }
    
    # Add current air quality if available
    if data.get("current", {}).get("air_quality") and aqi:
        forecast_info["current_weather"]["air_quality"] = data.get("current", {}).get("air_quality")
        logger.debug("Current air quality data included in response")
    
    # Process forecast days
    forecast_days = data.get("forecast", {}).get("forecastday", [])
    for day_data in forecast_days:
        day_info = {
            "date": day_data.get("date"),
            "date_epoch": day_data.get("date_epoch"),
            "day_summary": {
                "temperature": {
                    "max_c": day_data.get("day", {}).get("maxtemp_c"),
                    "max_f": day_data.get("day", {}).get("maxtemp_f"),
                    "min_c": day_data.get("day", {}).get("mintemp_c"),
                    "min_f": day_data.get("day", {}).get("mintemp_f"),
                    "avg_c": day_data.get("day", {}).get("avgtemp_c"),
                    "avg_f": day_data.get("day", {}).get("avgtemp_f"),
                },
                "condition": {
                    "text": day_data.get("day", {}).get("condition", {}).get("text"),
                    "icon": day_data.get("day", {}).get("condition", {}).get("icon"),
                    "code": day_data.get("day", {}).get("condition", {}).get("code"),
                },
                "wind": {
                    "max_speed_kph": day_data.get("day", {}).get("maxwind_kph"),
                    "max_speed_mph": day_data.get("day", {}).get("maxwind_mph"),
                },
                "precipitation": {
                    "total_mm": day_data.get("day", {}).get("totalprecip_mm"),
                    "total_in": day_data.get("day", {}).get("totalprecip_in"),
                    "total_snow_cm": day_data.get("day", {}).get("totalsnow_cm"),
                    "chance_of_rain": day_data.get("day", {}).get("daily_chance_of_rain"),
                    "chance_of_snow": day_data.get("day", {}).get("daily_chance_of_snow"),
                    "will_it_rain": day_data.get("day", {}).get("daily_will_it_rain"),
                    "will_it_snow": day_data.get("day", {}).get("daily_will_it_snow"),
                },
                "atmospheric": {
                    "avg_humidity": day_data.get("day", {}).get("avghumidity"),
                    "avg_visibility_km": day_data.get("day", {}).get("avgvis_km"),
                    "avg_visibility_miles": day_data.get("day", {}).get("avgvis_miles"),
                    "uv_index": day_data.get("day", {}).get("uv"),
                }
            },
            "astronomy": {
                "sunrise": day_data.get("astro", {}).get("sunrise"),
                "sunset": day_data.get("astro", {}).get("sunset"),
                "moonrise": day_data.get("astro", {}).get("moonrise"),
                "moonset": day_data.get("astro", {}).get("moonset"),
                "moon_phase": day_data.get("astro", {}).get("moon_phase"),
                "moon_illumination": day_data.get("astro", {}).get("moon_illumination"),
                "is_moon_up": day_data.get("astro", {}).get("is_moon_up"),
                "is_sun_up": day_data.get("astro", {}).get("is_sun_up"),
            },
            "hourly_forecast": []
        }
        
        # Add hourly forecast data
        hourly_data = day_data.get("hour", [])
        for hour_data in hourly_data:
            hour_info = {
                "time": hour_data.get("time"),
                "time_epoch": hour_data.get("time_epoch"),
                "temperature": {
                    "celsius": hour_data.get("temp_c"),
                    "fahrenheit": hour_data.get("temp_f"),
                    "feels_like_c": hour_data.get("feelslike_c"),
                    "feels_like_f": hour_data.get("feelslike_f"),
                    "windchill_c": hour_data.get("windchill_c"),
                    "windchill_f": hour_data.get("windchill_f"),
                    "heatindex_c": hour_data.get("heatindex_c"),
                    "heatindex_f": hour_data.get("heatindex_f"),
                    "dewpoint_c": hour_data.get("dewpoint_c"),
                    "dewpoint_f": hour_data.get("dewpoint_f"),
                },
                "condition": {
                    "text": hour_data.get("condition", {}).get("text"),
                    "icon": hour_data.get("condition", {}).get("icon"),
                    "code": hour_data.get("condition", {}).get("code"),
                },
                "wind": {
                    "speed_kph": hour_data.get("wind_kph"),
                    "speed_mph": hour_data.get("wind_mph"),
                    "direction": hour_data.get("wind_dir"),
                    "degree": hour_data.get("wind_degree"),
                    "gust_kph": hour_data.get("gust_kph"),
                    "gust_mph": hour_data.get("gust_mph"),
                },
                "precipitation": {
                    "mm": hour_data.get("precip_mm"),
                    "inches": hour_data.get("precip_in"),
                    "snow_cm": hour_data.get("snow_cm"),
                    "chance_of_rain": hour_data.get("chance_of_rain"),
                    "chance_of_snow": hour_data.get("chance_of_snow"),
                    "will_it_rain": hour_data.get("will_it_rain"),
                    "will_it_snow": hour_data.get("will_it_snow"),
                },
                "atmospheric": {
                    "humidity": hour_data.get("humidity"),
                    "pressure_mb": hour_data.get("pressure_mb"),
                    "pressure_in": hour_data.get("pressure_in"),
                    "visibility_km": hour_data.get("vis_km"),
                    "visibility_miles": hour_data.get("vis_miles"),
                    "cloud_cover": hour_data.get("cloud"),
                    "uv_index": hour_data.get("uv"),
                },
                "is_day": hour_data.get("is_day"),
            }
            
            # Add air quality data for this hour if available
            if hour_data.get("air_quality") and aqi:
                hour_info["air_quality"] = hour_data.get("air_quality")
            
            day_info["hourly_forecast"].append(hour_info)
        
        forecast_info["forecast"]["days"].append(day_info)
    
    # Add weather alerts if available
    if data.get("alerts") and alerts:
        forecast_info["alerts"] = {
            "alert_count": len(data.get("alerts", {}).get("alert", [])),
            "alerts": data.get("alerts", {}).get("alert", [])
        }
        logger.debug(f"Weather alerts included: {len(data.get('alerts', {}).get('alert', []))} alerts")
    
    logger.info(f"Weather forecast data successfully formatted for {len(forecast_days)} days")
    return forecast_info


def tool_get_historical_weather(location: str, date: str, aqi: bool = False) -> Dict:
    """
    Get historical weather data for a specific date.
    
    Args:
        location (str): Location query (city name, zipcode, coordinates, etc.)
        date (str): Date in YYYY-MM-DD format (on or after 2010-01-01)
        aqi (bool): Include air quality data (default False, available from 2021-03-01)
    
    Returns:
        Dict: Historical weather data
    """
    logger.info(f"Getting historical weather for location: {location} on date: {date}")
    
    if not WEATHERAPI_KEY:
        logger.error("WEATHERAPI_KEY is not set in environment variables")
        return {"error": "WEATHERAPI_KEY is not set in environment variables"}
    
    try:
        # Validate date format
        from datetime import datetime
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            logger.error(f"Invalid date format: {date}. Expected YYYY-MM-DD")
            return {"error": "Invalid date format. Expected YYYY-MM-DD"}
        
        url = "https://api.weatherapi.com/v1/history.json"
        params = {
            "key": WEATHERAPI_KEY,
            "q": location,
            "dt": date,
            "aqi": "yes" if aqi else "no"
        }
        
        logger.debug(f"Making request to WeatherAPI history: {url}")
        logger.debug(f"Request parameters: {params}")
        
        r = requests.get(url, params=params, timeout=15)
        
        logger.debug(f"WeatherAPI history response status: {r.status_code}")
        
        if r.status_code >= 400:
            logger.error(f"WeatherAPI history error {r.status_code}: {r.text}")
            return {"error": f"WeatherAPI history error {r.status_code}", "details": r.text}
        
        data = r.json()
        logger.debug("WeatherAPI history response received successfully")
        
        # Extract location name for logging
        location_name = data.get("location", {}).get("name", "Unknown")
        country = data.get("location", {}).get("country", "Unknown")
        logger.info(f"Historical weather data retrieved for: {location_name}, {country}")
        
        # Format historical weather response similar to forecast
        forecast_day = data.get("forecast", {}).get("forecastday", [])
        if not forecast_day:
            logger.error("No historical data found in response")
            return {"error": "No historical data found"}
        
        day_data = forecast_day[0]  # Historical data returns single day
        
        historical_info = {
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
            "date": day_data.get("date"),
            "date_epoch": day_data.get("date_epoch"),
            "day_summary": {
                "temperature": {
                    "max_c": day_data.get("day", {}).get("maxtemp_c"),
                    "max_f": day_data.get("day", {}).get("maxtemp_f"),
                    "min_c": day_data.get("day", {}).get("mintemp_c"),
                    "min_f": day_data.get("day", {}).get("mintemp_f"),
                    "avg_c": day_data.get("day", {}).get("avgtemp_c"),
                    "avg_f": day_data.get("day", {}).get("avgtemp_f"),
                },
                "condition": {
                    "text": day_data.get("day", {}).get("condition", {}).get("text"),
                    "icon": day_data.get("day", {}).get("condition", {}).get("icon"),
                    "code": day_data.get("day", {}).get("condition", {}).get("code"),
                },
                "wind": {
                    "max_speed_kph": day_data.get("day", {}).get("maxwind_kph"),
                    "max_speed_mph": day_data.get("day", {}).get("maxwind_mph"),
                },
                "precipitation": {
                    "total_mm": day_data.get("day", {}).get("totalprecip_mm"),
                    "total_in": day_data.get("day", {}).get("totalprecip_in"),
                    "total_snow_cm": day_data.get("day", {}).get("totalsnow_cm"),
                },
                "atmospheric": {
                    "avg_humidity": day_data.get("day", {}).get("avghumidity"),
                    "avg_visibility_km": day_data.get("day", {}).get("avgvis_km"),
                    "avg_visibility_miles": day_data.get("day", {}).get("avgvis_miles"),
                    "uv_index": day_data.get("day", {}).get("uv"),
                }
            },
            "astronomy": {
                "sunrise": day_data.get("astro", {}).get("sunrise"),
                "sunset": day_data.get("astro", {}).get("sunset"),
                "moonrise": day_data.get("astro", {}).get("moonrise"),
                "moonset": day_data.get("astro", {}).get("moonset"),
                "moon_phase": day_data.get("astro", {}).get("moon_phase"),
                "moon_illumination": day_data.get("astro", {}).get("moon_illumination"),
                "is_moon_up": day_data.get("astro", {}).get("is_moon_up"),
                "is_sun_up": day_data.get("astro", {}).get("is_sun_up"),
            },
            "hourly_data": []
        }
        
        # Add hourly historical data
        hourly_data = day_data.get("hour", [])
        for hour_data in hourly_data:
            hour_info = {
                "time": hour_data.get("time"),
                "time_epoch": hour_data.get("time_epoch"),
                "temperature": {
                    "celsius": hour_data.get("temp_c"),
                    "fahrenheit": hour_data.get("temp_f"),
                    "feels_like_c": hour_data.get("feelslike_c"),
                    "feels_like_f": hour_data.get("feelslike_f"),
                    "windchill_c": hour_data.get("windchill_c"),
                    "windchill_f": hour_data.get("windchill_f"),
                    "heatindex_c": hour_data.get("heatindex_c"),
                    "heatindex_f": hour_data.get("heatindex_f"),
                    "dewpoint_c": hour_data.get("dewpoint_c"),
                    "dewpoint_f": hour_data.get("dewpoint_f"),
                },
                "condition": {
                    "text": hour_data.get("condition", {}).get("text"),
                    "icon": hour_data.get("condition", {}).get("icon"),
                    "code": hour_data.get("condition", {}).get("code"),
                },
                "wind": {
                    "speed_kph": hour_data.get("wind_kph"),
                    "speed_mph": hour_data.get("wind_mph"),
                    "direction": hour_data.get("wind_dir"),
                    "degree": hour_data.get("wind_degree"),
                    "gust_kph": hour_data.get("gust_kph"),
                    "gust_mph": hour_data.get("gust_mph"),
                },
                "precipitation": {
                    "mm": hour_data.get("precip_mm"),
                    "inches": hour_data.get("precip_in"),
                    "snow_cm": hour_data.get("snow_cm"),
                },
                "atmospheric": {
                    "humidity": hour_data.get("humidity"),
                    "pressure_mb": hour_data.get("pressure_mb"),
                    "pressure_in": hour_data.get("pressure_in"),
                    "visibility_km": hour_data.get("vis_km"),
                    "visibility_miles": hour_data.get("vis_miles"),
                    "cloud_cover": hour_data.get("cloud"),
                    "uv_index": hour_data.get("uv"),
                },
                "is_day": hour_data.get("is_day"),
            }
            
            # Add air quality data for this hour if available
            if hour_data.get("air_quality") and aqi:
                hour_info["air_quality"] = hour_data.get("air_quality")
            
            historical_info["hourly_data"].append(hour_info)
        
        logger.info(f"Historical weather data successfully formatted for {date}")
        return historical_info
        
    except requests.RequestException as e:
        logger.error(f"Network error calling WeatherAPI history: {str(e)}")
        return {"error": f"Network error calling WeatherAPI history: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error calling WeatherAPI history: {str(e)}", exc_info=True)
        return {"error": f"Unexpected error calling WeatherAPI history: {str(e)}"}