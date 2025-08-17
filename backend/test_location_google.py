#!/usr/bin/env python3
"""
Test script for the updated Google Maps location tool.
"""

import os
import asyncio
import sys
sys.path.append('src')

# Set up a test API key (you'll need to replace this with your actual key)
# os.environ['GOOGLE_MAPS_API_KEY'] = 'your-google-maps-api-key-here'

async def test_location_tool():
    """Test the location tool functions"""
    from agents.tools.location_tool import (
        reverse_geocode_google,
        geocode_address_google,
        get_google_maps_api_key
    )
    
    print("Testing Google Maps Location Tool")
    print("=" * 40)
    
    # Check if API key is configured
    api_key = get_google_maps_api_key()
    if not api_key:
        print("⚠️  GOOGLE_MAPS_API_KEY environment variable not set")
        print("Please set your Google Maps API key before running tests:")
        print("export GOOGLE_MAPS_API_KEY='your-api-key-here'")
        return
    
    print(f"✅ Google Maps API key configured: {api_key[:10]}...")
    print()
    
    # Test 1: Reverse geocoding (coordinates to address)
    print("Test 1: Reverse Geocoding")
    print("-" * 25)
    
    # Test coordinates for Vadodara, Gujarat (approximately)
    test_coordinates = [
        (22.3072, 73.1812),  # Vadodara, Gujarat
        (28.6139, 77.2090),  # New Delhi
        (19.0760, 72.8777),  # Mumbai
    ]
    
    for lat, lon in test_coordinates:
        print(f"Testing coordinates: ({lat}, {lon})")
        try:
            result = await reverse_geocode_google(lat, lon)
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ City: {result.get('city', 'N/A')}")
                print(f"   State: {result.get('state', 'N/A')}")
                print(f"   Country: {result.get('country', 'N/A')}")
                print(f"   Address: {result.get('formatted_address', 'N/A')}")
        except Exception as e:
            print(f"❌ Exception: {e}")
        print()
    
    # Test 2: Forward geocoding (address to coordinates)
    print("Test 2: Forward Geocoding (Address to Coordinates)")
    print("-" * 50)
    
    test_addresses = [
        "Vadodara, Gujarat, India",
        "Mumbai, Maharashtra, India",
        "New Delhi, India",
        "123 Main Street, New York, NY, USA",
    ]
    
    for address in test_addresses:
        print(f"Testing address: {address}")
        try:
            result = await geocode_address_google(address)
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
            else:
                coords = result.get('coordinates', {})
                lat = coords.get('latitude', 'N/A')
                lon = coords.get('longitude', 'N/A')
                print(f"✅ Coordinates: ({lat}, {lon})")
                print(f"   City: {result.get('city', 'N/A')}")
                print(f"   State: {result.get('state', 'N/A')}")
                print(f"   Country: {result.get('country', 'N/A')}")
        except Exception as e:
            print(f"❌ Exception: {e}")
        print()

def test_sync_functions():
    """Test the synchronous wrapper functions"""
    from agents.tools.location_tool import (
        get_location_sync,
        geocode_address_sync,
        reverse_geocode_sync
    )
    
    print("Test 3: Synchronous Function Wrappers")
    print("-" * 37)
    
    # Test get_location_sync with query
    print("Testing get_location_sync with address query...")
    try:
        result = get_location_sync("Vadodara, Gujarat")
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ City: {result.get('city', 'N/A')}")
            print(f"   State: {result.get('state', 'N/A')}")
            print(f"   Country: {result.get('country', 'N/A')}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print()
    
    # Test reverse_geocode_sync
    print("Testing reverse_geocode_sync...")
    try:
        result = reverse_geocode_sync(22.3072, 73.1812)
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ City: {result.get('city', 'N/A')}")
            print(f"   State: {result.get('state', 'N/A')}")
            print(f"   Country: {result.get('country', 'N/A')}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print()

if __name__ == "__main__":
    print("Google Maps Location Tool Test")
    print("=" * 50)
    print()
    
    # Run async tests
    try:
        asyncio.run(test_location_tool())
    except Exception as e:
        print(f"❌ Error running async tests: {e}")
    
    print()
    
    # Run sync tests
    try:
        test_sync_functions()
    except Exception as e:
        print(f"❌ Error running sync tests: {e}")
    
    print("Test completed!")
