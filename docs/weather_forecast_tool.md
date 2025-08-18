# Weather Forecast Tool Documentation

The weather forecast tool provides comprehensive weather data using the WeatherAPI.com service. This tool extends the existing weather functionality with forecast capabilities, alerts, and historical data.

## Features

### Current Weather
- Real-time weather conditions
- Temperature (Celsius and Fahrenheit)
- Feels-like temperature
- Wind speed and direction
- Humidity, pressure, visibility
- UV index
- Air quality data (optional)

### Weather Forecast
- Up to 14 days forecast
- Daily summaries with min/max temperatures
- Hourly forecasts (24 hours per day)
- Precipitation probability and amounts
- Weather conditions and icons
- Astronomy data (sunrise, sunset, moon phases)
- Weather alerts
- Air quality forecasts

### Weather Alerts
- Government-issued weather warnings
- Severity levels and urgency information
- Affected areas and instructions
- Alert effectiveness periods

### Historical Weather
- Weather data from 2010-01-01 onwards
- Daily and hourly historical data
- Air quality history (from 2021-03-01)

## Available Functions

### 1. `tool_get_weather_by_coords(lat, lon)`
Get current weather by coordinates.

**Parameters:**
- `lat` (float): Latitude
- `lon` (float): Longitude

**Example:**
```python
from app.modules.tools.weather_tool import tool_get_weather_by_coords

# Get current weather for New York
weather = tool_get_weather_by_coords(40.7128, -74.0060)
print(f"Temperature: {weather['current_weather']['temperature']['celsius']}°C")
```

### 2. `tool_get_weather_forecast(lat, lon, days=3, alerts=True, aqi=True)`
Get weather forecast by coordinates.

**Parameters:**
- `lat` (float): Latitude
- `lon` (float): Longitude
- `days` (int): Number of forecast days (1-14, default 3)
- `alerts` (bool): Include weather alerts (default True)
- `aqi` (bool): Include air quality data (default True)

**Example:**
```python
from app.modules.tools.weather_tool import tool_get_weather_forecast

# Get 7-day forecast for London
forecast = tool_get_weather_forecast(51.5074, -0.1278, days=7)
for day in forecast['forecast']['days']:
    print(f"{day['date']}: {day['day_summary']['temperature']['max_c']}°C")
```

### 3. `tool_get_weather_forecast_by_location(location, days=3, alerts=True, aqi=True)`
Get weather forecast by location name.

**Parameters:**
- `location` (str): Location query (city name, zipcode, coordinates, etc.)
- `days` (int): Number of forecast days (1-14, default 3)
- `alerts` (bool): Include weather alerts (default True)
- `aqi` (bool): Include air quality data (default True)

**Example:**
```python
from app.modules.tools.weather_tool import tool_get_weather_forecast_by_location

# Get forecast for Tokyo
forecast = tool_get_weather_forecast_by_location("Tokyo", days=5)
print(f"Location: {forecast['location']['name']}")
```

### 4. `tool_get_weather_alerts(location)`
Get weather alerts for a specific location.

**Parameters:**
- `location` (str): Location query (city name, zipcode, coordinates, etc.)

**Example:**
```python
from app.modules.tools.weather_tool import tool_get_weather_alerts

# Get alerts for Miami
alerts = tool_get_weather_alerts("Miami, FL")
print(f"Alert count: {alerts['alerts']['alert_count']}")
```

### 5. `tool_get_historical_weather(location, date, aqi=False)`
Get historical weather data for a specific date.

**Parameters:**
- `location` (str): Location query (city name, zipcode, coordinates, etc.)
- `date` (str): Date in YYYY-MM-DD format (on or after 2010-01-01)
- `aqi` (bool): Include air quality data (default False, available from 2021-03-01)

**Example:**
```python
from app.modules.tools.weather_tool import tool_get_historical_weather

# Get historical weather for Paris on a specific date
historical = tool_get_historical_weather("Paris", "2024-01-15")
print(f"Max temp: {historical['day_summary']['temperature']['max_c']}°C")
```

## Response Structure

### Current Weather Response
```json
{
  "location": {
    "name": "New York",
    "region": "New York",
    "country": "United States of America",
    "coordinates": {"lat": 40.71, "lon": -74.01},
    "timezone": "America/New_York",
    "local_time": "2024-08-18 14:30"
  },
  "current_weather": {
    "temperature": {
      "celsius": 25.0,
      "fahrenheit": 77.0,
      "feels_like_c": 27.0,
      "feels_like_f": 80.6
    },
    "condition": {
      "text": "Partly cloudy",
      "icon": "//cdn.weatherapi.com/weather/64x64/day/116.png"
    },
    "wind": {
      "speed_kph": 15.0,
      "speed_mph": 9.3,
      "direction": "NW",
      "degree": 315
    },
    "atmospheric": {
      "humidity": 65,
      "pressure_mb": 1013.0,
      "visibility_km": 10.0,
      "uv_index": 5.0
    }
  }
}
```

### Forecast Response
The forecast response includes all current weather data plus:
```json
{
  "forecast": {
    "days": [
      {
        "date": "2024-08-18",
        "day_summary": {
          "temperature": {
            "max_c": 28.0,
            "min_c": 18.0,
            "avg_c": 23.0
          },
          "condition": {
            "text": "Partly cloudy",
            "icon": "//cdn.weatherapi.com/weather/64x64/day/116.png"
          },
          "precipitation": {
            "total_mm": 2.5,
            "chance_of_rain": 30,
            "will_it_rain": 1
          }
        },
        "astronomy": {
          "sunrise": "06:15 AM",
          "sunset": "07:45 PM",
          "moon_phase": "Waxing Crescent"
        },
        "hourly_forecast": [
          // 24 hourly data points
        ]
      }
    ]
  },
  "alerts": {
    "alert_count": 1,
    "alerts": [
      {
        "headline": "Thunderstorm Warning",
        "severity": "Moderate",
        "event": "Thunderstorm Warning",
        "description": "...",
        "effective": "2024-08-18T14:00:00-04:00",
        "expires": "2024-08-18T22:00:00-04:00"
      }
    ]
  }
}
```

## Setup Requirements

1. **API Key**: Sign up at [WeatherAPI.com](https://www.weatherapi.com/signup.aspx) to get your free API key.

2. **Environment Variable**: Set your API key in the environment:
   ```bash
   export WEATHERAPI_KEY="your-api-key-here"
   ```

3. **Dependencies**: The tool requires:
   - `requests` library
   - `python-dotenv` (for loading environment variables)

## API Limits

### Free Plan
- 1 million API calls per month
- Current weather, 3-day forecast
- No historical data
- No air quality data

### Paid Plans
- Higher API limits
- Up to 14-day forecasts
- Historical weather data
- Air quality data
- Marine weather
- Weather alerts

## Error Handling

All functions return error information in case of failures:
```json
{
  "error": "Error description",
  "details": "Additional error details if available"
}
```

Common errors:
- Missing or invalid API key
- Location not found
- Invalid date format (for historical data)
- API rate limit exceeded
- Network connectivity issues

## Agricultural Use Cases

The weather forecast tool is particularly useful for agricultural applications:

1. **Crop Planning**: Use forecasts to plan planting and harvesting schedules
2. **Irrigation Management**: Monitor precipitation forecasts to optimize watering
3. **Pest Control**: Weather conditions affect pest activity patterns
4. **Harvest Timing**: Temperature and precipitation forecasts help determine optimal harvest times
5. **Risk Assessment**: Weather alerts provide early warning for severe weather events
6. **Historical Analysis**: Compare current conditions with historical data for better decision making

## Testing

Run the test suite to verify functionality:
```bash
python test_weather_forecast.py
```

Make sure to set your `WEATHERAPI_KEY` environment variable before running tests.
