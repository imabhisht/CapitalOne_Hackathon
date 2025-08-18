"""
Agricultural data tool for accessing crop, irrigation, and climate data from MongoDB using geolocation.
"""
import os
import pymongo
from typing import Dict, List, Optional
from ...config import get_logger

# Initialize logger
logger = get_logger(__name__)

# MongoDB connection
MONGO_URL = os.getenv("MONGODB_URI")
database = None

if MONGO_URL:
    try:
        connection = pymongo.MongoClient(MONGO_URL)
        database = connection['agriculture_data']
        logger.info("Connected to MongoDB for agricultural data")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
else:
    logger.warning("MONGODB_URI not set, agricultural data tools will not be available")

def tool_get_crop_data_by_location(lat: float, lon: float, year: Optional[int] = None) -> Dict:
    """
    Get crop production data for the nearest location within 200 kilometers.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        year (int, optional): Specific year to query
        
    Returns:
        Dict: Crop production data
    """
    logger.info(f"Getting crop data for coordinates: {lat}, {lon}" + (f" for year {year}" if year else ""))
    
    if database is None:
        logger.error("Database not available")
        return {"error": "Database not available"}
    
    try:
        collection = database['crop_production_data']
        
        # Build geospatial query for points within 200km
        query = {
            "coordinates": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]  # GeoJSON format is [longitude, latitude]
                    },
                    "$maxDistance": 200000  # 200 kilometers in meters
                }
            }
        }
        
        if year:
            query["year"] = year
            
        # Sort by distance and year descending to get most recent data first
        cursor = collection.find(query).sort([("year", -1)])
        results = list(cursor)
        
        if not results:
            logger.warning(f"No crop data found within 200km of {lat}, {lon}")
            return {
                "success": False,
                "message": f"No crop data found within 200km of coordinates {lat}, {lon}",
                "latitude": lat,
                "longitude": lon
            }
        
        # Get the nearest result
        nearest_result = results[0]
        
        # If year is specified or only one result, return that
        if year or len(results) == 1:
            logger.info(f"Crop data retrieved for coordinates {lat}, {lon}, year {nearest_result.get('year', 'unknown')}")
            return {
                "success": True,
                "data": {
                    "year": nearest_result.get("year"),
                    "district": nearest_result.get("district"),
                    "state": nearest_result.get("state"),
                    "distance_km": nearest_result.get("distance_km", "unknown"),
                    "rice_area": nearest_result.get("rice"),
                    "wheat_area": nearest_result.get("wheat"),
                    "sorghum_area": nearest_result.get("sorghum"),
                    "pearl_millet_area": nearest_result.get("pearl_millet"),
                    "maize_area": nearest_result.get("maize"),
                    "fingermillet_area": nearest_result.get("fingermillet"),
                    "total_area": nearest_result.get("total_area")
                },
                "location": {
                    "latitude": nearest_result.get("latitude"),
                    "longitude": nearest_result.get("longitude"),
                    "district": nearest_result.get("district"),
                    "state": nearest_result.get("state")
                }
            }
        else:
            # Return data for multiple years from the same location
            # Find all results from the same district and state as the nearest result
            location_query = {
                "district": nearest_result.get("district"),
                "state": nearest_result.get("state")
            }
            
            if year:
                location_query["year"] = year
                
            location_cursor = collection.find(location_query).sort("year", -1)
            location_results = list(location_cursor)
            
            data_list = []
            for result in location_results:
                data_list.append({
                    "year": result.get("year"),
                    "district": result.get("district"),
                    "state": result.get("state"),
                    "rice_area": result.get("rice"),
                    "wheat_area": result.get("wheat"),
                    "sorghum_area": result.get("sorghum"),
                    "pearl_millet_area": result.get("pearl_millet"),
                    "maize_area": result.get("maize"),
                    "fingermillet_area": result.get("fingermillet"),
                    "total_area": result.get("total_area")
                })
            logger.info(f"Crop data retrieved for {nearest_result.get('district')}, {nearest_result.get('state')} for {len(data_list)} years")
            return {
                "success": True,
                "data": data_list,
                "count": len(data_list),
                "location": {
                    "latitude": nearest_result.get("latitude"),
                    "longitude": nearest_result.get("longitude"),
                    "district": nearest_result.get("district"),
                    "state": nearest_result.get("state")
                }
            }
            
    except Exception as e:
        logger.error(f"Error retrieving crop data: {str(e)}", exc_info=True)
        return {
            "error": f"Error retrieving crop data: {str(e)}",
            "latitude": lat,
            "longitude": lon
        }

def tool_get_irrigation_data_by_location(lat: float, lon: float, year: Optional[int] = None) -> Dict:
    """
    Get irrigation source data for the nearest location within 200 kilometers.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        year (int, optional): Specific year to query
        
    Returns:
        Dict: Irrigation data
    """
    logger.info(f"Getting irrigation data for coordinates: {lat}, {lon}" + (f" for year {year}" if year else ""))
    
    if database is None:
        logger.error("Database not available")
        return {"error": "Database not available"}
    
    try:
        collection = database['irrigation_source_data']
        
        # Build geospatial query for points within 200km
        query = {
            "coordinates": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]  # GeoJSON format is [longitude, latitude]
                    },
                    "$maxDistance": 200000  # 200 kilometers in meters
                }
            }
        }
        
        if year:
            query["year"] = year
            
        # Sort by distance and year descending to get most recent data first
        cursor = collection.find(query).sort([("year", -1)])
        results = list(cursor)
        
        if not results:
            logger.warning(f"No irrigation data found within 200km of {lat}, {lon}")
            return {
                "success": False,
                "message": f"No irrigation data found within 200km of coordinates {lat}, {lon}",
                "latitude": lat,
                "longitude": lon
            }
        
        # Get the nearest result
        nearest_result = results[0]
        
        # If year is specified or only one result, return that
        if year or len(results) == 1:
            logger.info(f"Irrigation data retrieved for coordinates {lat}, {lon}, year {nearest_result.get('year', 'unknown')}")
            return {
                "success": True,
                "data": {
                    "year": nearest_result.get("year"),
                    "district": nearest_result.get("district"),
                    "state": nearest_result.get("state"),
                    "distance_km": nearest_result.get("distance_km", "unknown"),
                    "canals_area": nearest_result.get("canals_area"),
                    "tanks_area": nearest_result.get("tanks_area"),
                    "tube_wells_area": nearest_result.get("tube_wells_area"),
                    "other_wells_area": nearest_result.get("other_wells_area"),
                    "total_well_area": nearest_result.get("total_well_area"),
                    "other_sources_area": nearest_result.get("other_sources_area")
                },
                "location": {
                    "latitude": nearest_result.get("latitude"),
                    "longitude": nearest_result.get("longitude"),
                    "district": nearest_result.get("district"),
                    "state": nearest_result.get("state")
                }
            }
        else:
            # Return data for multiple years from the same location
            # Find all results from the same district and state as the nearest result
            location_query = {
                "district": nearest_result.get("district"),
                "state": nearest_result.get("state")
            }
            
            if year:
                location_query["year"] = year
                
            location_cursor = collection.find(location_query).sort("year", -1)
            location_results = list(location_cursor)
            
            data_list = []
            for result in location_results:
                data_list.append({
                    "year": result.get("year"),
                    "district": result.get("district"),
                    "state": result.get("state"),
                    "canals_area": result.get("canals_area"),
                    "tanks_area": result.get("tanks_area"),
                    "tube_wells_area": result.get("tube_wells_area"),
                    "other_wells_area": result.get("other_wells_area"),
                    "total_well_area": result.get("total_well_area"),
                    "other_sources_area": result.get("other_sources_area")
                })
            logger.info(f"Irrigation data retrieved for {nearest_result.get('district')}, {nearest_result.get('state')} for {len(data_list)} years")
            return {
                "success": True,
                "data": data_list,
                "count": len(data_list),
                "location": {
                    "latitude": nearest_result.get("latitude"),
                    "longitude": nearest_result.get("longitude"),
                    "district": nearest_result.get("district"),
                    "state": nearest_result.get("state")
                }
            }
            
    except Exception as e:
        logger.error(f"Error retrieving irrigation data: {str(e)}", exc_info=True)
        return {
            "error": f"Error retrieving irrigation data: {str(e)}",
            "latitude": lat,
            "longitude": lon
        }

def tool_get_climate_data_by_location(lat: float, lon: float, data_type: str = "temperature", year: Optional[int] = None) -> Dict:
    """
    Get climate data (temperature or precipitation) for the nearest location within 200 kilometers.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        data_type (str): Type of climate data ("temperature" or "precipitation")
        year (int, optional): Specific year to query
        
    Returns:
        Dict: Climate data
    """
    logger.info(f"Getting {data_type} data for coordinates: {lat}, {lon}" + (f" for year {year}" if year else ""))
    
    if database is None:
        logger.error("Database not available")
        return {"error": "Database not available"}
    
    # Validate data type
    if data_type not in ["temperature", "precipitation"]:
        logger.error(f"Invalid data_type: {data_type}")
        return {"error": f"Invalid data_type: {data_type}. Must be 'temperature' or 'precipitation'"}
    
    try:
        # For temperature, we need to handle max and min temperature data
        if data_type == "temperature":
            # First try to get max temperature data
            collection = database['max_temperature_data']
        else:
            collection_name = f"{data_type}_data"
            collection = database[collection_name]
        
        # Build geospatial query for points within 200km
        query = {
            "coordinates": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]  # GeoJSON format is [longitude, latitude]
                    },
                    "$maxDistance": 200000  # 200 kilometers in meters
                }
            }
        }
        
        if year:
            query["year"] = year
            
        # Sort by distance and year descending to get most recent data first
        cursor = collection.find(query).sort([("year", -1)])
        results = list(cursor)
        
        # If no max temperature data, try min temperature data
        if data_type == "temperature" and not results:
            collection = database['min_temperature_data']
            cursor = collection.find(query).sort([("year", -1)])
            results = list(cursor)
        
        if not results:
            logger.warning(f"No {data_type} data found within 200km of {lat}, {lon}")
            return {
                "success": False,
                "message": f"No {data_type} data found within 200km of coordinates {lat}, {lon}",
                "latitude": lat,
                "longitude": lon,
                "data_type": data_type
            }
        
        # Get the nearest result
        nearest_result = results[0]
        
        # If year is specified or only one result, return that
        if year or len(results) == 1:
            logger.info(f"{data_type.capitalize()} data retrieved for coordinates {lat}, {lon}, year {nearest_result.get('year', 'unknown')}")
            
            # Format the data
            data = {
                "year": nearest_result.get("year"),
                "district": nearest_result.get("district"),
                "state": nearest_result.get("state"),
                "distance_km": nearest_result.get("distance_km", "unknown")
            }
            
            # Add monthly data
            months = ["january", "february", "march", "april", "may", "june",
                     "july", "august", "september", "october", "november", "december"]
            
            for month in months:
                data[month] = nearest_result.get(month)
                
            return {
                "success": True,
                "data": data,
                "data_type": data_type,
                "location": {
                    "latitude": nearest_result.get("latitude"),
                    "longitude": nearest_result.get("longitude"),
                    "district": nearest_result.get("district"),
                    "state": nearest_result.get("state")
                }
            }
        else:
            # Return data for multiple years from the same location
            # Find all results from the same district and state as the nearest result
            location_query = {
                "district": nearest_result.get("district"),
                "state": nearest_result.get("state")
            }
            
            if year:
                location_query["year"] = year
                
            location_cursor = collection.find(location_query).sort("year", -1)
            location_results = list(location_cursor)
            
            # Format the data for multiple years
            data_list = []
            for result in location_results:
                data = {
                    "year": result.get("year"),
                    "district": result.get("district"),
                    "state": result.get("state")
                }
                
                # Add monthly data
                months = ["january", "february", "march", "april", "may", "june",
                         "july", "august", "september", "october", "november", "december"]
                
                for month in months:
                    data[month] = result.get(month)
                    
                data_list.append(data)
                
            logger.info(f"{data_type.capitalize()} data retrieved for {nearest_result.get('district')}, {nearest_result.get('state')} for {len(data_list)} years")
            return {
                "success": True,
                "data": data_list,
                "count": len(data_list),
                "data_type": data_type,
                "location": {
                    "latitude": nearest_result.get("latitude"),
                    "longitude": nearest_result.get("longitude"),
                    "district": nearest_result.get("district"),
                    "state": nearest_result.get("state")
                }
            }
            
    except Exception as e:
        logger.error(f"Error retrieving {data_type} data: {str(e)}", exc_info=True)
        return {
            "error": f"Error retrieving {data_type} data: {str(e)}",
            "latitude": lat,
            "longitude": lon,
            "data_type": data_type
        }