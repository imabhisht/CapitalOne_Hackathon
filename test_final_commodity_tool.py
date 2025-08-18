"""
Final test script demonstrating the full commodity price functionality.
"""
import os
import sys
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

# Load environment variables
load_dotenv()

from app.modules.tools.commodity_tool import tool_get_commodity_price_by_name_and_location

def test_full_workflow():
    """Test the full commodity price workflow"""
    print("Testing full commodity price workflow...")
    
    # Test cases with different commodities and locations
    test_cases = [
        {
            "commodity_name": "Wheat",
            "state_name": "Maharashtra",
            "district_name": "Nagpur",
            "description": "Wheat prices in Nagpur, Maharashtra"
        },
        {
            "commodity_name": "Rice",
            "state_name": "West Bengal",
            "district_name": "Kolkata",
            "description": "Rice prices in Kolkata, West Bengal"
        },
        {
            "commodity_name": "Cotton",
            "state_name": "Gujarat",
            "district_name": "Ahmedabad",
            "description": "Cotton prices in Ahmedabad, Gujarat"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['description']}")
        
        result = tool_get_commodity_price_by_name_and_location(
            commodity_name=test_case["commodity_name"],
            state_name=test_case["state_name"],
            district_name=test_case["district_name"],
            from_date="2025-07-18",
            to_date="2025-08-18"
        )
        
        if result.get("error"):
            print(f"   Error: {result['error']}")
        else:
            print(f"   Success: Retrieved {result.get('count', 0)} price records")
            if result.get('prices'):
                # Show first price record as example
                first_price = result['prices'][0]
                print(f"   Latest price: {first_price['market']} - ₹{first_price['modal_price']} per quintal")
                print(f"   Date: {first_price['date']}")
                print(f"   Price range: ₹{first_price['min_price']} - ₹{first_price['max_price']} per quintal")

if __name__ == "__main__":
    test_full_workflow()