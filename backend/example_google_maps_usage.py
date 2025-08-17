#!/usr/bin/env python3
"""
Example showing how to use the updated Google Maps location tool.
"""

import os
import sys
import asyncio

# Add the backend src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def main():
    """Main example function"""
    
    # IMPORTANT: Set your Google Maps API key first
    # You can get one from: https://console.cloud.google.com/
    
    if not os.getenv('GOOGLE_MAPS_API_KEY'):
        print("❌ Please set GOOGLE_MAPS_API_KEY environment variable")
        print("   Get your API key from: https://console.cloud.google.com/")
        print("   Then run: export GOOGLE_MAPS_API_KEY='your-api-key-here'")
        return
    
    # Import the tools
    from agents.tools.location_tool import (
        get_location,
        geocode_address, 
        reverse_geocode,
        get_location_sync
    )
    
    print("🗺️  Google Maps Location Tool Examples")
    print("=" * 50)
    
    # Example 1: Get location with a query (uses geocoding)
    print("\n1️⃣  Get location with address query:")
    try:
        result = await get_location("Vadodara, Gujarat, India")
        if 'error' not in result:
            print(f"   ✅ Found: {result.get('city')}, {result.get('state')}, {result.get('country')}")
            print(f"   📍 Coordinates: {result.get('coordinates', {}).get('latitude')}, {result.get('coordinates', {}).get('longitude')}")
        else:
            print(f"   ❌ Error: {result['error']}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Example 2: Geocode a specific address
    print("\n2️⃣  Geocode a specific address:")
    try:
        result = await geocode_address("1600 Amphitheatre Parkway, Mountain View, CA")
        if 'error' not in result:
            print(f"   ✅ Found: {result.get('city')}, {result.get('state')}, {result.get('country')}")
            print(f"   📍 Coordinates: {result.get('coordinates', {}).get('latitude')}, {result.get('coordinates', {}).get('longitude')}")
            print(f"   📍 Full Address: {result.get('formatted_address')}")
        else:
            print(f"   ❌ Error: {result['error']}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Example 3: Reverse geocode coordinates
    print("\n3️⃣  Reverse geocode coordinates:")
    try:
        # Coordinates for Mumbai, India
        result = await reverse_geocode(19.0760, 72.8777)
        if 'error' not in result:
            print(f"   ✅ Found: {result.get('city')}, {result.get('state')}, {result.get('country')}")
            print(f"   📍 Full Address: {result.get('formatted_address')}")
        else:
            print(f"   ❌ Error: {result['error']}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Example 4: Using synchronous version (for compatibility)
    print("\n4️⃣  Using synchronous version:")
    try:
        result = get_location_sync("New Delhi, India")
        if 'error' not in result:
            print(f"   ✅ Found: {result.get('city')}, {result.get('state')}, {result.get('country')}")
        else:
            print(f"   ❌ Error: {result['error']}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Example 5: Error handling - invalid coordinates
    print("\n5️⃣  Error handling example:")
    try:
        result = await reverse_geocode(999, 999)  # Invalid coordinates
        if 'error' in result:
            print(f"   ✅ Properly handled error: {result['error']}")
        else:
            print(f"   ❓ Unexpected success: {result}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n✅ Examples completed!")
    print("\n📝 Notes:")
    print("   • All hardcoded locations have been removed")
    print("   • The tool now uses real Google Maps data")
    print("   • Works worldwide, not just for India")
    print("   • Maintains compatibility with existing code")

if __name__ == "__main__":
    asyncio.run(main())
