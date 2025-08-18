"""
Simple test script for the soil water content tool

This script tests the soil water content tool functions directly
without importing the full app module dependencies.
"""
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Test the functions directly
def test_swc_tool():
    """Test soil water content tool functions directly"""
    
    print("=" * 80)
    print("TESTING SOIL WATER CONTENT TOOL")
    print("=" * 80)
    
    # Test coordinates (agricultural area in Iowa, USA)
    test_lat = 41.5868
    test_lon = -93.6250
    
    print(f"\nTest Location: {test_lat}, {test_lon} (Iowa, USA)")
    print("-" * 50)
    
    # Test the product info function (doesn't require external API calls)
    print("\n1. Testing SWC product information...")
    
    try:
        # Import the specific function
        from app.modules.tools.soil_water_content_tool import tool_get_swc_product_info
        
        result = tool_get_swc_product_info()
        print("✓ Success")
        print(f"   Service: {result.get('service_overview', {}).get('name', 'N/A')}")
        print(f"   Available Resolutions: {list(result.get('available_products', {}).keys())}")
        print(f"   Number of Applications: {len(result.get('key_applications', {}))}")
        
        # Show some key details
        if 'key_applications' in result:
            print("\n   Key Application Areas:")
            for area, apps in result['key_applications'].items():
                print(f"     - {area.title()}: {len(apps)} use cases")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test soil analysis function
    print("\n2. Testing soil condition analysis...")
    
    try:
        from app.modules.tools.soil_water_content_tool import tool_analyze_soil_conditions
        
        result = tool_analyze_soil_conditions(
            test_lat, test_lon, 
            crop_type="corn", 
            season="summer"
        )
        print("✓ Success")
        print(f"   Crop Type: {result.get('analysis_parameters', {}).get('crop_type', 'N/A')}")
        print(f"   Season: {result.get('analysis_parameters', {}).get('season', 'N/A')}")
        print(f"   Resolution: {result.get('analysis_parameters', {}).get('resolution', 'N/A')}")
        
        # Show agricultural recommendations
        if 'agricultural_recommendations' in result:
            print("\n   Agricultural Recommendations Available:")
            for key in result['agricultural_recommendations'].keys():
                print(f"     - {key.replace('_', ' ').title()}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test soil water content query (shows what data would be available)
    print("\n3. Testing soil water content query...")
    
    try:
        from app.modules.tools.soil_water_content_tool import tool_get_soil_water_content
        
        result = tool_get_soil_water_content(test_lat, test_lon, resolution="100m", sensor="smap")
        print("✓ Success")
        print(f"   Product ID: {result.get('product_info', {}).get('id', 'N/A')}")
        print(f"   Resolution: {result.get('product_info', {}).get('resolution', 'N/A')}")
        print(f"   Sensor: {result.get('product_info', {}).get('sensor', 'N/A')}")
        print(f"   Status: {result.get('status', 'N/A')}")
        
        # Show use cases
        if 'use_cases' in result:
            print(f"\n   Available Use Cases ({len(result['use_cases'])}):")
            for use_case in result['use_cases']:
                print(f"     - {use_case}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test error handling
    print("\n4. Testing error handling...")
    
    try:
        from app.modules.tools.soil_water_content_tool import tool_get_soil_water_content
        
        # Test with invalid resolution
        result = tool_get_soil_water_content(test_lat, test_lon, resolution="invalid", sensor="smap")
        if 'error' in result:
            print("✓ Error handling works correctly")
            print(f"   Expected error: {result['error']}")
        else:
            print("✗ Error handling failed - should have returned error")
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)
    
    # Display available products
    print("\n5. Available SWC Products:")
    print("-" * 30)
    
    try:
        from app.modules.tools.soil_water_content_tool import SWC_PRODUCTS
        
        for resolution, sensors in SWC_PRODUCTS.items():
            print(f"\n{resolution} Resolution:")
            for sensor, product_id in sensors.items():
                print(f"  {sensor.upper()}: {product_id}")
        
    except Exception as e:
        print(f"Error displaying products: {e}")

if __name__ == "__main__":
    test_swc_tool()
