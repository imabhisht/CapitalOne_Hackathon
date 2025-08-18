#!/usr/bin/env python3
"""
Quick test to see what geographies are available in CEDA database
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

# Load environment variables
load_dotenv()

from app.modules.tools.commodity_tool import tool_get_geographies

def main():
    """Get available geographies"""
    print("🚀 Getting available geographies from CEDA database...")
    
    result = tool_get_geographies()
    
    if result.get("success"):
        geographies = result.get("geographies", [])
        print(f"✅ Found {len(geographies)} states")
        
        # Look for Maharashtra
        for state in geographies:
            if "maharashtra" in state.get("state_name", "").lower():
                print(f"\n📍 Found Maharashtra: {state.get('state_name')}")
                districts = state.get("districts", [])
                print(f"   Districts ({len(districts)}):")
                for district in districts[:10]:  # Show first 10
                    print(f"   - {district.get('district_name')}")
                if len(districts) > 10:
                    print(f"   ... and {len(districts) - 10} more districts")
                break
        
        # Look for states containing "nagpur"
        print("\n🔍 Searching for Nagpur in all districts...")
        found_nagpur = False
        for state in geographies:
            districts = state.get("districts", [])
            for district in districts:
                district_name = district.get("district_name", "")
                if "nagpur" in district_name.lower():
                    print(f"   Found: {district_name} in {state.get('state_name')}")
                    found_nagpur = True
        
        if not found_nagpur:
            print("   No districts containing 'nagpur' found")
            
    else:
        print(f"❌ Failed to get geographies: {result.get('error')}")

if __name__ == "__main__":
    main()
