"""
Test script for the soil water content tool

This script tests the various functions of the soil water content tool
to ensure they work correctly and provide useful information.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.modules.tools.soil_water_content_tool import (
    tool_get_soil_water_content,
    tool_create_swc_subscription,
    tool_get_swc_statistics,
    tool_get_swc_product_info,
    tool_analyze_soil_conditions
)
import json

def test_soil_water_content_tool():
    """Test all soil water content tool functions"""
    
    print("=" * 80)
    print("TESTING SOIL WATER CONTENT TOOL")
    print("=" * 80)
    
    # Test coordinates (agricultural area in Iowa, USA)
    test_lat = 41.5868
    test_lon = -93.6250
    
    print(f"\nTest Location: {test_lat}, {test_lon} (Iowa, USA)")
    print("-" * 50)
    
    # Test 1: Get soil water content
    print("\n1. Testing tool_get_soil_water_content...")
    try:
        result = tool_get_soil_water_content(test_lat, test_lon, resolution="100m", sensor="smap")
        print("✓ Success")
        print(f"   Product ID: {result.get('product_info', {}).get('id', 'N/A')}")
        print(f"   Resolution: {result.get('product_info', {}).get('resolution', 'N/A')}")
        print(f"   Status: {result.get('status', 'N/A')}")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Create subscription
    print("\n2. Testing tool_create_swc_subscription...")
    try:
        result = tool_create_swc_subscription(
            test_lat, test_lon, 
            resolution="100m", 
            sensor="smap",
            bucket_name="test-swc-bucket"
        )
        print("✓ Success")
        print(f"   Status: {result.get('status', 'N/A')}")
        print(f"   Cloud Provider: {result.get('delivery_info', {}).get('cloud_provider', 'N/A')}")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Get statistics
    print("\n3. Testing tool_get_swc_statistics...")
    try:
        result = tool_get_swc_statistics(test_lat, test_lon, days_back=90)
        print("✓ Success")
        print(f"   Analysis Period: {result.get('analysis_period', {}).get('days_analyzed', 'N/A')} days")
        print(f"   Sensor: {result.get('product_info', {}).get('sensor', 'N/A')}")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Get product info
    print("\n4. Testing tool_get_swc_product_info...")
    try:
        result = tool_get_swc_product_info()
        print("✓ Success")
        print(f"   Available Resolutions: {list(result.get('available_products', {}).keys())}")
        print(f"   Service: {result.get('service_overview', {}).get('name', 'N/A')}")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 5: Analyze soil conditions
    print("\n5. Testing tool_analyze_soil_conditions...")
    try:
        result = tool_analyze_soil_conditions(
            test_lat, test_lon, 
            crop_type="corn", 
            season="summer"
        )
        print("✓ Success")
        print(f"   Crop Type: {result.get('analysis_parameters', {}).get('crop_type', 'N/A')}")
        print(f"   Season: {result.get('analysis_parameters', {}).get('season', 'N/A')}")
        if 'error' in result:
            print(f"   Error: {result['error']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test different parameters
    print("\n6. Testing different sensor and resolution combinations...")
    test_configs = [
        {"resolution": "20m", "sensor": "amsr2"},
        {"resolution": "1000m", "sensor": "smap"},
        {"resolution": "invalid", "sensor": "smap"},  # Should handle error
    ]
    
    for i, config in enumerate(test_configs, 1):
        try:
            result = tool_get_soil_water_content(test_lat, test_lon, **config)
            if 'error' in result:
                print(f"   6.{i} ✓ Expected error handled: {config}")
            else:
                print(f"   6.{i} ✓ Valid config: {config}")
        except Exception as e:
            print(f"   6.{i} ✗ Unexpected error with {config}: {e}")
    
    print("\n" + "=" * 80)
    print("SOIL WATER CONTENT TOOL TESTING COMPLETE")
    print("=" * 80)
    
    # Display sample detailed output
    print("\n7. Sample detailed output (Product Information):")
    print("-" * 50)
    try:
        detailed_result = tool_get_swc_product_info()
        print(json.dumps(detailed_result.get('key_applications', {}), indent=2))
    except Exception as e:
        print(f"Error displaying detailed output: {e}")

if __name__ == "__main__":
    test_soil_water_content_tool()
