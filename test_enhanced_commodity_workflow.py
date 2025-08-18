#!/usr/bin/env python3
"""
Test script for the enhanced commodity price workflow.
Tests the complete flow from user query to getting commodity prices.
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# Load environment variables
load_dotenv()

from app.modules.tools.commodity_tool import (
    tool_get_commodity_price_by_name_and_location,
    tool_get_commodity_price_by_location_and_name,
    tool_intelligent_commodity_price_query,
    reverse_geocode_with_google_maps
)

def test_reverse_geocoding():
    """Test reverse geocoding functionality"""
    print("Testing reverse geocoding...")
    
    # Test coordinates for Nagpur, Maharashtra
    lat, lon = 21.1458, 79.0882
    
    result = reverse_geocode_with_google_maps(lat, lon)
    if result:
        state, district = result
        print(f"✅ Reverse geocoding successful: {district}, {state}")
        return state, district
    else:
        print("❌ Reverse geocoding failed")
        return None, None

def test_commodity_price_by_name_and_location():
    """Test getting commodity prices by name and location"""
    print("\nTesting commodity price by name and location...")
    
    result = tool_get_commodity_price_by_name_and_location(
        commodity_name="Cotton",
        state_name="Maharashtra", 
        district_name="Nagpur"
    )
    
    if result.get("success"):
        print("✅ Commodity price by name and location successful")
        print(f"Found {result.get('count', 0)} price records")
        prices = result.get('prices', [])
        if prices:
            latest_price = prices[0]
            print(f"Latest price: ₹{latest_price.get('modal_price', 'N/A')} per quintal at {latest_price.get('market', 'Unknown market')}")
    else:
        print(f"❌ Commodity price by name and location failed: {result.get('error')}")
    
    return result

def test_commodity_price_by_location_and_name():
    """Test getting commodity prices by coordinates and name"""
    print("\nTesting commodity price by location and name...")
    
    # Coordinates for Nagpur, Maharashtra
    lat, lon = 21.1458, 79.0882
    
    result = tool_get_commodity_price_by_location_and_name(
        commodity_name="Cotton",
        lat=lat,
        lon=lon
    )
    
    if result.get("success"):
        print("✅ Commodity price by location and name successful")
        print(f"Found {result.get('count', 0)} price records")
        location = result.get('location', {})
        print(f"Detected location: {location.get('district')}, {location.get('state')}")
    else:
        print(f"❌ Commodity price by location and name failed: {result.get('error')}")
    
    return result

def test_intelligent_commodity_query():
    """Test intelligent commodity price query"""
    print("\nTesting intelligent commodity price query...")
    
    test_queries = [
        "What is the price of cotton in Maharashtra?",
        "cotton rates in nagpur",
        "price of rice",
        "what's the current cotton price"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        result = tool_intelligent_commodity_price_query(
            query=query,
            lat=21.1458,  # Nagpur coordinates
            lon=79.0882,
            user_location="Nagpur, Maharashtra"
        )
        
        if result.get("success"):
            print(f"✅ Query successful: Found {result.get('count', 0)} price records")
        else:
            print(f"❌ Query failed: {result.get('error')}")

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced Commodity Tool Workflow Tests")
    print("=" * 60)
    
    # Check if required API keys are available
    ceda_key = os.getenv("CEDA_API_KEY")
    gmaps_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    print(f"CEDA API Key: {'✅ Available' if ceda_key else '❌ Missing'}")
    print(f"Google Maps API Key: {'✅ Available' if gmaps_key else '❌ Missing'}")
    
    if not ceda_key:
        print("\n❌ CEDA_API_KEY is required for commodity price testing")
        return
    
    if not gmaps_key:
        print("\n⚠️ GOOGLE_MAPS_API_KEY is missing - reverse geocoding tests will fail")
    
    print("\n" + "=" * 60)
    
    # Test 1: Reverse Geocoding
    state, district = test_reverse_geocoding()
    
    # Test 2: Commodity price by name and location
    test_commodity_price_by_name_and_location()
    
    # Test 3: Commodity price by location and name (with reverse geocoding)
    test_commodity_price_by_location_and_name()
    
    # Test 4: Intelligent commodity query
    test_intelligent_commodity_query()
    
    print("\n" + "=" * 60)
    print("🏁 Tests completed!")

if __name__ == "__main__":
    main()
