#!/usr/bin/env python3
"""
Test script to debug the crop data query issue.
"""

import os
import pymongo
import logging
from typing import Dict, Any, Optional
import dotenv

dotenv.load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_crop_data_query():
    """Test the crop data query with the actual document format"""
    try:
        # Get MongoDB URI from environment
        mongodb_uri = os.getenv("MONGODB_URI")
        if not mongodb_uri:
            print("Error: MONGODB_URI environment variable not set")
            return
        
        print(f"Connecting to MongoDB...")
        client = pymongo.MongoClient(mongodb_uri)
        db = client.get_database("agriculture_data")
        collection = db.get_collection("crop_production_data")
        
        # Check collection exists and has documents
        doc_count = collection.count_documents({})
        print(f"Total documents in collection: {doc_count}")
        
        if doc_count == 0:
            print("No documents found in collection!")
            return
        
        # Check for documents with coordinates
        coords_count = collection.count_documents({"coordinates": {"$exists": True}})
        print(f"Documents with coordinates: {coords_count}")
        
        # Show a sample document
        sample_doc = collection.find_one({"coordinates": {"$exists": True}})
        if sample_doc:
            print(f"Sample document coordinates: {sample_doc.get('coordinates')}")
            print(f"Sample document district: {sample_doc.get('district')}, state: {sample_doc.get('state')}")
        
        # Check indexes
        print("\nCurrent indexes:")
        indexes = list(collection.list_indexes())
        has_geo_index = False
        for idx in indexes:
            print(f"  {idx}")
            if 'coordinates' in str(idx):
                has_geo_index = True
        
        # Create index if it doesn't exist
        if not has_geo_index:
            print("\nCreating 2dsphere index on coordinates field...")
            try:
                collection.create_index([("coordinates", "2dsphere")])
                print("✓ Index created successfully")
            except Exception as e:
                print(f"✗ Failed to create index: {e}")
                return
        else:
            print("✓ Geospatial index exists")
        
        # Test the query - using coordinates from the sample document
        test_longitude = 70.1327524  # Jamnagar longitude
        test_latitude = 22.32997     # Jamnagar latitude
        
        print(f"\nTesting query with coordinates: [{test_longitude}, {test_latitude}]")
        
        # Try different query approaches
        
        # Approach 1: Using $near with GeoJSON (current approach)
        print("\n1. Testing $near with GeoJSON Point:")
        query1 = {
            "coordinates": {
                "$near": {
                    "$geometry": {
                        "type": "Point", 
                        "coordinates": [test_longitude, test_latitude]
                    },
                    "$maxDistance": 20000  # 20km
                }
            }
        }
        try:
            results1 = list(collection.find(query1).limit(5))
            print(f"   Results: {len(results1)} documents found")
            if results1:
                for i, doc in enumerate(results1):
                    print(f"   Doc {i+1}: {doc.get('district')}, {doc.get('state')} - coords: {doc.get('coordinates')}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Approach 2: Using $nearSphere
        print("\n2. Testing $nearSphere:")
        query2 = {
            "coordinates": {
                "$nearSphere": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [test_longitude, test_latitude]
                    },
                    "$maxDistance": 20000
                }
            }
        }
        try:
            results2 = list(collection.find(query2).limit(5))
            print(f"   Results: {len(results2)} documents found")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Approach 3: Using $geoWithin with $centerSphere (more forgiving)
        print("\n3. Testing $geoWithin with $centerSphere:")
        # Convert 20km to radians (Earth radius ~6371 km)
        radius_in_radians = 20 / 6371
        query3 = {
            "coordinates": {
                "$geoWithin": {
                    "$centerSphere": [[test_longitude, test_latitude], radius_in_radians]
                }
            }
        }
        try:
            results3 = list(collection.find(query3).limit(5))
            print(f"   Results: {len(results3)} documents found")
            if results3:
                for i, doc in enumerate(results3):
                    print(f"   Doc {i+1}: {doc.get('district')}, {doc.get('state')} - coords: {doc.get('coordinates')}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Approach 4: Simple exact match test
        print("\n4. Testing exact coordinate match:")
        query4 = {"coordinates": [test_longitude, test_latitude]}
        try:
            results4 = list(collection.find(query4).limit(5))
            print(f"   Results: {len(results4)} documents found")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Approach 5: Test with a broader area around Jamnagar
        print("\n5. Testing broader area search:")
        query5 = {
            "coordinates": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [test_longitude, test_latitude]
                    },
                    "$maxDistance": 100000  # 100km
                }
            }
        }
        try:
            results5 = list(collection.find(query5).limit(5))
            print(f"   Results: {len(results5)} documents found")
            if results5:
                for i, doc in enumerate(results5):
                    coords = doc.get('coordinates', [])
                    if len(coords) == 2:
                        # Calculate rough distance
                        import math
                        lat1, lon1 = test_latitude, test_longitude
                        lat2, lon2 = coords[1], coords[0]
                        
                        # Rough distance calculation
                        dlat = math.radians(lat2 - lat1)
                        dlon = math.radians(lon2 - lon1)
                        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
                             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
                             math.sin(dlon/2) * math.sin(dlon/2))
                        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                        distance = 6371 * c  # Earth radius in km
                        
                        print(f"   Doc {i+1}: {doc.get('district')}, {doc.get('state')} - coords: {coords} - ~{distance:.1f}km")
        except Exception as e:
            print(f"   Error: {e}")
        
        client.close()
        print("\nTest completed!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_crop_data_query()
