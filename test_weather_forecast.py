#!/usr/bin/env python3
"""
Test script for the enhanced weather forecast tool
"""
import os
import sys
from datetime import datetime, timedelta
import json

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.modules.tools.weather_tool import (
    tool_get_weather_by_coords,
    tool_get_weather_forecast,
    tool_get_weather_forecast_by_location,
    tool_get_weather_alerts,
    tool_get_historical_weather
)

def test_current_weather():
    """Test current weather by coordinates"""
    print("=== Testing Current Weather by Coordinates ===")
    # Test with New York coordinates
    result = tool_get_weather_by_coords(lat=40.7128, lon=-74.0060)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Location: {result['location']['name']}, {result['location']['country']}")
        print(f"Temperature: {result['current_weather']['temperature']['celsius']}°C")
        print(f"Condition: {result['current_weather']['condition']['text']}")
        print(f"Humidity: {result['current_weather']['atmospheric']['humidity']}%")
    print()

def test_forecast_by_coordinates():
    """Test weather forecast by coordinates"""
    print("=== Testing Weather Forecast by Coordinates ===")
    # Test with London coordinates
    result = tool_get_weather_forecast(lat=51.5074, lon=-0.1278, days=3)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Location: {result['location']['name']}, {result['location']['country']}")
        print(f"Current Temperature: {result['current_weather']['temperature']['celsius']}°C")
        print(f"Forecast Days: {len(result['forecast']['days'])}")
        
        for i, day in enumerate(result['forecast']['days']):
            print(f"Day {i+1} ({day['date']}):")
            print(f"  Max: {day['day_summary']['temperature']['max_c']}°C")
            print(f"  Min: {day['day_summary']['temperature']['min_c']}°C")
            print(f"  Condition: {day['day_summary']['condition']['text']}")
            print(f"  Rain Chance: {day['day_summary']['precipitation']['chance_of_rain']}%")
        
        if "alerts" in result:
            print(f"Weather Alerts: {result['alerts']['alert_count']}")
    print()

def test_forecast_by_location():
    """Test weather forecast by location name"""
    print("=== Testing Weather Forecast by Location Name ===")
    result = tool_get_weather_forecast_by_location("Tokyo", days=5)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Location: {result['location']['name']}, {result['location']['country']}")
        print(f"Forecast Days: {len(result['forecast']['days'])}")
        
        for i, day in enumerate(result['forecast']['days'][:3]):  # Show first 3 days
            print(f"Day {i+1} ({day['date']}):")
            print(f"  Max: {day['day_summary']['temperature']['max_c']}°C")
            print(f"  Min: {day['day_summary']['temperature']['min_c']}°C")
            print(f"  Condition: {day['day_summary']['condition']['text']}")
    print()

def test_weather_alerts():
    """Test weather alerts"""
    print("=== Testing Weather Alerts ===")
    # Test with a location that might have alerts
    result = tool_get_weather_alerts("Miami, FL")
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Location: {result['location']['name']}, {result['location']['country']}")
        print(f"Alert Count: {result['alerts']['alert_count']}")
        
        if result['alerts']['alert_count'] > 0:
            for alert in result['alerts']['alerts']:
                print(f"Alert: {alert['headline']}")
                print(f"Severity: {alert['severity']}")
                print(f"Event: {alert['event']}")
        else:
            print("No weather alerts at this time.")
    print()

def test_historical_weather():
    """Test historical weather"""
    print("=== Testing Historical Weather ===")
    # Test with a date from last week
    yesterday = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    result = tool_get_historical_weather("Paris", yesterday)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Location: {result['location']['name']}, {result['location']['country']}")
        print(f"Date: {result['date']}")
        print(f"Max Temperature: {result['day_summary']['temperature']['max_c']}°C")
        print(f"Min Temperature: {result['day_summary']['temperature']['min_c']}°C")
        print(f"Condition: {result['day_summary']['condition']['text']}")
        print(f"Total Precipitation: {result['day_summary']['precipitation']['total_mm']}mm")
        print(f"Hourly Data Points: {len(result['hourly_data'])}")
    print()

def main():
    """Run all tests"""
    print("Weather Forecast Tool Test Suite")
    print("=" * 50)
    
    # Check if API key is set
    if not os.getenv("WEATHERAPI_KEY"):
        print("ERROR: WEATHERAPI_KEY environment variable is not set!")
        print("Please set your WeatherAPI key before running tests.")
        sys.exit(1)
    
    try:
        test_current_weather()
        test_forecast_by_coordinates()
        test_forecast_by_location()
        test_weather_alerts()
        test_historical_weather()
        
        print("All tests completed!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
