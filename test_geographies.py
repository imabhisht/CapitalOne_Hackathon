"""
Test script to check available states and districts.
"""
import os
import sys
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

# Load environment variables
load_dotenv()

from app.modules.tools.commodity_tool import tool_get_geographies

def test_geographies():
    """Test the geographies tool"""
    print("Testing geographies retrieval...")
    
    result = tool_get_geographies()
    if result.get("error"):
        print(f"Error: {result['error']}")
        return
    
    geographies = result.get("geographies", [])
    print(f"Found {len(geographies)} states")
    
    # Print first few states and their districts
    for i, state in enumerate(geographies[:5]):
        print(f"State {i+1}: {state.get('state_name')} (ID: {state.get('state_id')})")
        districts = state.get("districts", [])
        print(f"  Districts ({len(districts)}):")
        for j, district in enumerate(districts[:3]):
            print(f"    {j+1}. {district.get('district_name')} (ID: {district.get('district_id')})")
        if len(districts) > 3:
            print(f"    ... and {len(districts) - 3} more districts")
        print()

if __name__ == "__main__":
    test_geographies()