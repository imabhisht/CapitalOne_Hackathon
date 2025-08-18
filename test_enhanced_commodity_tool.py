"""
Test script for the enhanced CEDA commodity tool.
"""
import os
import sys
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

# Load environment variables
load_dotenv()

from app.modules.tools.commodity_tool import tool_get_commodity_list, tool_get_commodity_price_by_name_and_location

def test_enhanced_commodity_tool():
    """Test the enhanced commodity tool"""
    print("Testing enhanced CEDA commodity tool...")
    
    # First, test if we can get the commodity list
    print("\n1. Testing commodity list retrieval...")
    commodities_result = tool_get_commodity_list()
    
    if commodities_result.get("error"):
        print(f"   Error: {commodities_result['error']}")
        return
    else:
        print(f"   Success: Retrieved {len(commodities_result.get('commodities', []))} commodities")
        if commodities_result.get('commodities'):
            print(f"   Available commodities: {[c['name'] for c in commodities_result['commodities'][:5]]}")
    
    # Test getting commodity prices by name and location
    print("\n2. Testing commodity price retrieval by name and location...")
    if commodities_result.get('commodities'):
        # Use the first available commodity for testing
        first_commodity = commodities_result['commodities'][0]['name']
        print(f"   Using '{first_commodity}' for testing...")
        
        result = tool_get_commodity_price_by_name_and_location(
            commodity_name=first_commodity,
            state_name="Maharashtra",
            district_name="Nagpur",
            from_date="2025-07-18",
            to_date="2025-08-18"
        )
        
        if result.get("error"):
            print(f"   Error: {result['error']}")
        else:
            print(f"   Success: Retrieved {result.get('count', 0)} price records")
            if result.get('prices'):
                print(f"   Sample price: {result['prices'][0] if result['prices'] else 'None'}")

if __name__ == "__main__":
    test_enhanced_commodity_tool()