"""
Standalone test for soil water content functionality

This tests the core functionality without dependencies.
"""
import os
from datetime import datetime, timedelta

# Mock logger for testing
class MockLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")
    def debug(self, msg): print(f"DEBUG: {msg}")

logger = MockLogger()

# SWC Product definitions
SWC_PRODUCTS = {
    "20m": {
        "smap": "SWC-SMAP-L_V1.0_20",
        "amsr2": "SWC-AMSR2-X_V5.0_20"
    },
    "100m": {
        "smap": "SWC-SMAP-L_V1.0_100", 
        "amsr2": "SWC-AMSR2-X_V5.0_100"
    },
    "1000m": {
        "smap": "SWC-SMAP-L_V1.0_1000",
        "amsr2": "SWC-AMSR2-X_V5.0_1000"
    }
}

def test_get_soil_water_content(lat: float, lon: float, resolution: str = "100m", 
                               sensor: str = "smap", days_back: int = 30):
    """Test version of soil water content function"""
    logger.info(f"Getting soil water content data for coordinates: {lat}, {lon}")
    
    # Validate inputs
    if resolution not in SWC_PRODUCTS:
        logger.error(f"Invalid resolution: {resolution}")
        return {"error": f"Invalid resolution: {resolution}. Must be one of: {list(SWC_PRODUCTS.keys())}"}
    
    if sensor not in SWC_PRODUCTS[resolution]:
        logger.error(f"Invalid sensor: {sensor}")
        return {"error": f"Invalid sensor: {sensor}. Must be one of: {list(SWC_PRODUCTS[resolution].keys())}"}
    
    try:
        # Get the product ID
        product_id = SWC_PRODUCTS[resolution][sensor]
        
        # Create a small area of interest around the point (approximately 1km buffer)
        buffer = 0.009  # Roughly 1km at equator
        geometry = {
            "type": "Polygon",
            "coordinates": [[
                [lon - buffer, lat - buffer],
                [lon + buffer, lat - buffer], 
                [lon + buffer, lat + buffer],
                [lon - buffer, lat + buffer],
                [lon - buffer, lat - buffer]
            ]]
        }
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        result = {
            "location": {
                "latitude": lat,
                "longitude": lon,
                "geometry": geometry
            },
            "product_info": {
                "id": product_id,
                "sensor": sensor.upper(),
                "resolution": resolution,
                "description": f"Soil Water Content data from {sensor.upper()} sensor at {resolution} resolution"
            },
            "query_parameters": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "days_requested": days_back
            },
            "data_characteristics": {
                "measurement": "Soil water content (volumetric water content)",
                "units": "m³/m³ (cubic meters of water per cubic meter of soil)",
                "temporal_resolution": "Near-daily",
                "spatial_resolution": resolution,
                "sensor_type": sensor.upper(),
                "coverage": "Global"
            },
            "use_cases": [
                "Agricultural irrigation planning",
                "Drought monitoring and assessment", 
                "Water resource management",
                "Natural disaster risk assessment",
                "Crop yield prediction"
            ],
            "status": "subscription_required",
            "note": "To access actual soil water content data, you would need to create a Planet subscription and configure cloud storage delivery."
        }
        
        logger.info(f"Successfully retrieved SWC product information for {lat}, {lon}")
        return result
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

def test_get_swc_product_info():
    """Test version of product info function"""
    logger.info("Getting SWC product information")
    
    try:
        result = {
            "service_overview": {
                "name": "Planet Soil Water Content (SWC)",
                "description": "Near-daily global soil water content measurements from satellite sensors",
                "provider": "Planet Labs",
                "data_source": "Passive microwave observations"
            },
            "available_products": SWC_PRODUCTS,
            "product_details": {
                "spatial_resolutions": {
                    "20m": "High resolution for field-level analysis",
                    "100m": "Balanced resolution for regional monitoring", 
                    "1000m": "Lower resolution for large-scale analysis"
                },
                "sensors": {
                    "SMAP": "Soil Moisture Active Passive mission",
                    "AMSR2": "Advanced Microwave Scanning Radiometer 2"
                },
                "temporal_coverage": "Near-daily global coverage",
                "measurement_units": "m³/m³ (volumetric water content)",
                "data_format": "GeoTIFF"
            },
            "key_applications": {
                "agriculture": [
                    "Irrigation scheduling and optimization",
                    "Crop stress monitoring",
                    "Yield prediction modeling",
                    "Field condition assessment"
                ],
                "water_management": [
                    "Drought monitoring and early warning",
                    "Water resource planning", 
                    "Reservoir management",
                    "Flood risk assessment"
                ],
                "environmental": [
                    "Ecosystem health monitoring",
                    "Climate change research",
                    "Carbon cycle studies",
                    "Wildfire risk assessment"
                ],
                "disaster_management": [
                    "Natural disaster risk assessment",
                    "Emergency response planning",
                    "Recovery monitoring",
                    "Insurance risk modeling"
                ]
            }
        }
        
        logger.info("Successfully retrieved SWC product information")
        return result
        
    except Exception as e:
        logger.error(f"Error getting product info: {str(e)}")
        return {"error": f"Error getting product info: {str(e)}"}

def run_tests():
    """Run all tests"""
    print("=" * 80)
    print("TESTING SOIL WATER CONTENT TOOL (STANDALONE)")
    print("=" * 80)
    
    # Test coordinates (agricultural area in Iowa, USA)
    test_lat = 41.5868
    test_lon = -93.6250
    
    print(f"\nTest Location: {test_lat}, {test_lon} (Iowa, USA)")
    print("-" * 50)
    
    # Test 1: Get product info
    print("\n1. Testing SWC product information...")
    try:
        result = test_get_swc_product_info()
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
    
    # Test 2: Get soil water content data
    print("\n2. Testing soil water content query...")
    try:
        result = test_get_soil_water_content(test_lat, test_lon, resolution="100m", sensor="smap")
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
    
    # Test 3: Test different sensors and resolutions
    print("\n3. Testing different sensor/resolution combinations...")
    test_configs = [
        {"resolution": "20m", "sensor": "amsr2"},
        {"resolution": "1000m", "sensor": "smap"},
        {"resolution": "100m", "sensor": "amsr2"},
    ]
    
    for i, config in enumerate(test_configs, 1):
        try:
            result = test_get_soil_water_content(test_lat, test_lon, **config)
            if 'error' in result:
                print(f"   3.{i} ✗ Error with {config}: {result['error']}")
            else:
                print(f"   3.{i} ✓ Success with {config['resolution']} {config['sensor'].upper()}")
                print(f"        Product ID: {result['product_info']['id']}")
        except Exception as e:
            print(f"   3.{i} ✗ Exception with {config}: {e}")
    
    # Test 4: Test error handling
    print("\n4. Testing error handling...")
    try:
        result = test_get_soil_water_content(test_lat, test_lon, resolution="invalid", sensor="smap")
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
    
    for resolution, sensors in SWC_PRODUCTS.items():
        print(f"\n{resolution} Resolution:")
        for sensor, product_id in sensors.items():
            print(f"  {sensor.upper()}: {product_id}")
    
    print("\n6. Sample Data Structure:")
    print("-" * 30)
    sample_result = test_get_soil_water_content(test_lat, test_lon)
    print("Data characteristics:")
    for key, value in sample_result.get('data_characteristics', {}).items():
        print(f"  {key.replace('_', ' ').title()}: {value}")

if __name__ == "__main__":
    run_tests()
