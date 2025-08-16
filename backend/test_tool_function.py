#!/usr/bin/env python3
"""
Test the actual crop_data_tool function
"""

import os
import sys
sys.path.append('/Users/devsapariya/Documents/Code/my-code/hackathon-capital-one/CapitalOne_Hackathon/backend/src')

from agents.tools.crop_data_tool import get_crop_data

def test_crop_data_tool():
    """Test the crop data tool function directly"""
    
    # Test with Jamnagar coordinates (we know this works from the DB test)
    longitude = 70.1327524
    latitude = 22.32997
    
    print(f"Testing crop_data_tool with coordinates: [{longitude}, {latitude}]")
    
    # Test without year filter
    print("\n1. Testing without year filter:")
    result1 = get_crop_data(longitude, latitude)
    print(f"   Result type: {type(result1)}")
    print(f"   Keys: {list(result1.keys()) if isinstance(result1, dict) else 'Not a dict'}")
    
    if isinstance(result1, dict):
        if 'error' in result1:
            print(f"   Error: {result1['error']}")
        else:
            print(f"   Count: {result1.get('count', 'No count field')}")
            if 'results' in result1:
                results = result1['results']
                print(f"   Results length: {len(results) if isinstance(results, list) else 'Not a list'}")
                if isinstance(results, list) and len(results) > 0:
                    print(f"   First result district: {results[0].get('district', 'No district')}")
                    print(f"   First result state: {results[0].get('state', 'No state')}")
    
    # Test with year filter
    print("\n2. Testing with year filter (2020):")
    result2 = get_crop_data(longitude, latitude, 2020)
    print(f"   Result type: {type(result2)}")
    
    if isinstance(result2, dict):
        if 'error' in result2:
            print(f"   Error: {result2['error']}")
        else:
            print(f"   Count: {result2.get('count', 'No count field')}")
    
    # Test with coordinates that should have no results (middle of ocean)
    print("\n3. Testing with ocean coordinates (should return no results):")
    result3 = get_crop_data(0.0, 0.0)  # Gulf of Guinea
    print(f"   Result type: {type(result3)}")
    
    if isinstance(result3, dict):
        if 'error' in result3:
            print(f"   Error: {result3['error']}")
        else:
            print(f"   Count: {result3.get('count', 'No count field')}")

if __name__ == "__main__":
    test_crop_data_tool()
