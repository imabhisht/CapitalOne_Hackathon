"""
Crop Data Tool for querying crop production data from MongoDB.
"""

import os
from langchain_core.tools import tool
from typing import Dict, Any, Optional
import logging
import pymongo

logger = logging.getLogger(__name__)

@tool
def get_crop_data(longitude: float, latitude: float, year: Optional[int] = None) -> Dict[str, Any]:
    """
    Get the Data for the production of crops in a particular Area
    Args:
        longitude: Longitude coordinate
        latitude: Latitude coordinate
        year: Year (optional)
    Returns:
        Dict containing crop data or error message
    """
    try:
        collection = pymongo.MongoClient(os.getenv("MONGODB_URI")).get_database("agriculture_data").get_collection("crop_production_data")
        
        # Build query using the coordinates field that exists in the database
        query = {
            "coordinates": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "$maxDistance": 20000  # 20km radius
                }
            }
        }

        print(query)
        if year:
            query["year"] = year

        data = collection.find(query)  # Limit results for performance
        results = list(data)
        
        logger.info(f"Retrieved {len(results)} crop data records for query: {query}")
        return {"results": results, "query": query, "count": len(results)}
    except Exception as e:
        logger.error(f"Error getting crop data: {e}")
        return {"error": f"Failed to get crop data: {str(e)}"}
