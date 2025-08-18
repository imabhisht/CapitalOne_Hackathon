"""
Test script to check the raw geographies response.
"""
import os
import sys
from dotenv import load_dotenv
import requests

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

# Load environment variables
load_dotenv()

CEDA_API_BASE_URL = "https://api.ceda.ashoka.edu.in/v1"
CEDA_API_KEY = os.getenv("CEDA_API_KEY")

def get_ceda_api_headers():
    """Get headers for CEDA API requests"""
    return {
        "Authorization": f"Bearer {CEDA_API_KEY}",
        "Content-Type": "application/json"
    }

def test_raw_geographies():
    """Test the raw geographies API response"""
    print("Testing raw geographies API response...")
    
    if not CEDA_API_KEY:
        print("Error: CEDA_API_KEY not set")
        return
    
    try:
        url = f"{CEDA_API_BASE_URL}/agmarknet/geographies"
        response = requests.get(url, headers=get_ceda_api_headers(), timeout=30)
        
        if response.status_code == 200:
            raw_data = response.json()
            print("Raw response structure:")
            print(f"Keys: {raw_data.keys()}")
            
            output_data = raw_data.get("output", {})
            print(f"Output keys: {output_data.keys()}")
            
            data = output_data.get("data", [])
            print(f"Data type: {type(data)}")
            print(f"Data length: {len(data)}")
            
            # Print first few items
            for i, item in enumerate(data[:3]):
                print(f"Item {i+1}: {item}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_raw_geographies()