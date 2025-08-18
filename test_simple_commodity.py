#!/usr/bin/env python3
"""
Simple test with known working data to validate the enhanced commodity tool
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
    tool_intelligent_commodity_price_query
)

def test_direct_query():
    """Test with specific known locations"""
    print("🚀 Testing enhanced commodity tool with known locations...")
    
    # Try with some common state/district combinations
    test_cases = [
        ("Cotton", "Maharashtra", "Nagpur"),
        ("Cotton", "Gujarat", "Ahmedabad"),
        ("Rice", "West Bengal", "Kolkata"),
        ("Wheat", "Punjab", "Ludhiana")
    ]
    
    for commodity, state, district in test_cases:
        print(f"\n📍 Testing: {commodity} in {district}, {state}")
        
        result = tool_get_commodity_price_by_name_and_location(
            commodity_name=commodity,
            state_name=state,
            district_name=district
        )
        
        if result.get("success"):
            count = result.get('count', 0)
            print(f"✅ Success: Found {count} price records")
            if count > 0:
                prices = result.get('prices', [])
                if prices:
                    latest = prices[0]
                    print(f"   Latest: ₹{latest.get('modal_price', 'N/A')} at {latest.get('market', 'Unknown')}")
        else:
            error = result.get('error', 'Unknown error')
            print(f"❌ Failed: {error}")
            
            # If it's a location not found error, show suggestions
            if "not found" in error.lower():
                print("   This might be due to exact name matching issues")

def test_intelligent_query():
    """Test intelligent query parsing"""
    print("\n" + "="*60)
    print("🧠 Testing intelligent commodity query parsing...")
    
    # Test queries without coordinates to see how it handles them
    queries = [
        "cotton price",
        "what is rice price",
        "price of wheat"
    ]
    
    for query in queries:
        print(f"\n💬 Query: '{query}'")
        
        result = tool_intelligent_commodity_price_query(query=query)
        
        if result.get("success"):
            print(f"✅ Parsed successfully")
        else:
            error = result.get('error', 'Unknown error')
            print(f"❌ Error: {error}")

def main():
    """Run the tests"""
    # Check API key
    ceda_key = os.getenv("CEDA_API_KEY")
    if not ceda_key:
        print("❌ CEDA_API_KEY is required")
        return
    
    print(f"✅ CEDA API Key available")
    
    # Run tests with some delay to avoid rate limits
    test_direct_query()
    
    # Wait a bit to avoid rate limits
    print("\n⏱️ Waiting a moment to avoid rate limits...")
    import time
    time.sleep(2)
    
    test_intelligent_query()
    
    print("\n" + "="*60)
    print("🏁 Testing completed!")
    print("\n💡 Tips for using the enhanced commodity tool:")
    print("1. The tool now handles fuzzy matching for location names")
    print("2. Use 'intelligent_commodity_price_query' for natural language queries")
    print("3. Provide coordinates when possible for automatic location detection")
    print("4. The tool will suggest alternatives if exact matches aren't found")

if __name__ == "__main__":
    main()
