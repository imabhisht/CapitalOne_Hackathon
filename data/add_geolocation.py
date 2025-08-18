import pymongo
import os
import dotenv
import logging
import time
import requests
from typing import Dict, Tuple, Optional
import json

logging.basicConfig(level=logging.INFO)

dotenv.load_dotenv()

# MongoDB connection
connection = pymongo.MongoClient(os.getenv("MONGO_URL"))
database = connection['agriculture_data']

# Collection names
COLLECTIONS = [
    'crop_production_data',
    'irrigation_source_data',
    'max_temperature_data',
    'min_temperature_data',
    'precipitation_data'
]

class GeocodeCache:
    """Simple file-based cache for geocoding results to avoid repeated API calls"""
    
    def __init__(self, cache_file='geocode_cache.json'):
        self.cache_file = cache_file
        self.cache = self.load_cache()
    
    def load_cache(self) -> Dict:
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def get(self, key: str) -> Optional[Tuple[float, float]]:
        result = self.cache.get(key)
        if result:
            return tuple(result)
        return None
    
    def set(self, key: str, lat: float, lon: float):
        self.cache[key] = [lat, lon]
        self.save_cache()

def geocode_location(district: str, state: str, cache: GeocodeCache, use_google_maps_first: bool = False) -> Optional[Tuple[float, float]]:
    """
    Geocode a district and state to get latitude and longitude coordinates.
    Uses multiple geocoding strategies with automatic fallback.
    
    Args:
        district: District name
        state: State name  
        cache: GeocodeCache instance
        use_google_maps_first: If True, tries Google Maps first, then falls back to OpenStreetMap
                              If False, tries OpenStreetMap first, then falls back to Google Maps
    """
    if not district or not state:
        return None
    
    # Create cache key
    cache_key = f"{district.lower().strip()}, {state.lower().strip()}"
    
    # Check cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        logging.debug(f"Using cached coordinates for {cache_key}")
        return cached_result
    
    # Determine the order of geocoding services to try
    has_google_api_key = bool(os.getenv("GOOGLE_MAPS_API_KEY"))
    
    if use_google_maps_first and has_google_api_key:
        services = [
            ("Google Maps", geocode_with_google_maps),
            ("OpenStreetMap", geocode_with_nominatim)
        ]
    else:
        services = [
            ("OpenStreetMap", geocode_with_nominatim),
        ]
        if has_google_api_key:
            services.append(("Google Maps", geocode_with_google_maps))
    
    # Try each service in order
    for service_name, geocode_func in services:
        try:
            logging.debug(f"Trying {service_name} for {cache_key}")
            result = geocode_func(district, state, cache_key, cache)
            
            if result:
                logging.info(f"Successfully geocoded {cache_key} using {service_name}: {result}")
                return result
            else:
                logging.warning(f"{service_name} failed to geocode {cache_key}")
        
        except Exception as e:
            logging.warning(f"{service_name} error for {cache_key}: {e}")
            continue
    
    # All services failed
    logging.error(f"All geocoding services failed for {cache_key}")
    return None

def geocode_with_google_maps(district: str, state: str, cache_key: str, cache: GeocodeCache) -> Optional[Tuple[float, float]]:
    """Geocode using Google Maps API with enhanced error handling and retries"""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        logging.warning("Google Maps API key not found in environment variables")
        return None
    
    search_queries = [
        f"{district} District, {state}, India",
        f"{district}, {state}, India",
        f"{district} {state} India",
        f"{district} {state}"
    ]
    
    for query in search_queries:
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': query,
                'key': api_key,
                'region': 'in',  # Bias results to India
                'components': 'country:IN'  # Restrict to India
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['status'] == 'OK' and data['results']:
                    location = data['results'][0]['geometry']['location']
                    lat = float(location['lat'])
                    lon = float(location['lng'])
                    
                    # Validate coordinates are within reasonable bounds for India
                    if 6.0 <= lat <= 37.0 and 68.0 <= lon <= 98.0:
                        cache.set(cache_key, lat, lon)
                        logging.info(f"Google Maps geocoded {cache_key}: ({lat}, {lon})")
                        return (lat, lon)
                    else:
                        logging.warning(f"Google Maps returned coordinates outside India bounds for {cache_key}: ({lat}, {lon})")
                
                elif data['status'] == 'ZERO_RESULTS':
                    logging.debug(f"Google Maps found no results for query: {query}")
                    continue
                
                elif data['status'] == 'OVER_QUERY_LIMIT':
                    logging.error("Google Maps API quota exceeded")
                    return None
                
                else:
                    logging.warning(f"Google Maps API error: {data['status']} for query: {query}")
            
            elif response.status_code == 429:
                logging.warning("Google Maps API rate limit hit, waiting...")
                time.sleep(2)
                continue
            
            else:
                logging.warning(f"Google Maps API HTTP error {response.status_code} for query: {query}")
        
        except requests.exceptions.RequestException as e:
            logging.warning(f"Google Maps API request failed for {query}: {e}")
            continue
        except Exception as e:
            logging.warning(f"Google Maps API unexpected error for {query}: {e}")
            continue
        
        time.sleep(0.1)  # Small delay between queries to avoid rate limiting
    
    return None

def geocode_with_nominatim(district: str, state: str, cache_key: str, cache: GeocodeCache) -> Optional[Tuple[float, float]]:
    """Geocode using OpenStreetMap Nominatim with enhanced error handling and retries"""
    search_queries = [
        f"{district} District, {state}, India",
        f"{district}, {state}, India",
        f"{district} District, {state}",
        f"{district}, {state}",
        f"{district} {state} India",
        f"{district} {state}"
    ]
    
    headers = {
        'User-Agent': 'Agriculture Data Geocoder (contact: your-email@example.com)'
    }
    
    for query in search_queries:
        try:
            logging.debug(f"Nominatim trying query: {query}")
            
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': query,
                'format': 'json',
                'limit': 3,  # Get top 3 results to choose the best one
                'countrycodes': 'in',  # Restrict to India
                'addressdetails': 1,
                'bounded': 1,
                'viewbox': '68.0,6.0,98.0,37.0'  # Bounding box for India
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data:
                    # Find the best result (prefer results with district/state info)
                    best_result = None
                    for result in data:
                        lat = float(result['lat'])
                        lon = float(result['lon'])
                        
                        # Validate coordinates are within reasonable bounds for India
                        if 6.0 <= lat <= 37.0 and 68.0 <= lon <= 98.0:
                            # Check if this result has good administrative details
                            display_name = result.get('display_name', '').lower()
                            address = result.get('address', {})
                            
                            # Prefer results that mention the district or state
                            if (district.lower() in display_name or 
                                state.lower() in display_name or
                                address.get('state_district', '').lower() == district.lower()):
                                best_result = (lat, lon)
                                break
                            elif not best_result:
                                best_result = (lat, lon)
                    
                    if best_result:
                        lat, lon = best_result
                        cache.set(cache_key, lat, lon)
                        logging.info(f"Nominatim geocoded {cache_key}: ({lat}, {lon})")
                        return best_result
                
            elif response.status_code == 429:
                logging.warning("Nominatim rate limit hit, waiting...")
                time.sleep(5)
                continue
            
            else:
                logging.warning(f"Nominatim HTTP error {response.status_code} for query: {query}")
        
        except requests.exceptions.RequestException as e:
            logging.warning(f"Nominatim request failed for {query}: {e}")
            continue
        except Exception as e:
            logging.warning(f"Nominatim unexpected error for {query}: {e}")
            continue
        
        # Rate limiting - be respectful to the free service
        time.sleep(1.5)
    
    return None

def get_unique_locations(database) -> Dict[str, Tuple[str, str]]:
    """Get all unique district-state combinations from all collections"""
    unique_locations = {}
    
    for collection_name in COLLECTIONS:
        collection = database[collection_name]
        
        # Get unique district-state combinations
        pipeline = [
            {
                "$match": {
                    "district": {"$ne": None, "$exists": True},
                    "state": {"$ne": None, "$exists": True}
                }
            },
            {
                "$group": {
                    "_id": {
                        "district": "$district",
                        "state": "$state"
                    }
                }
            }
        ]
        
        results = collection.aggregate(pipeline)
        for result in results:
            district = result['_id']['district']
            state = result['_id']['state']
            if district and state:
                key = f"{district.lower().strip()}, {state.lower().strip()}"
                unique_locations[key] = (district, state)
    
    return unique_locations

def create_geospatial_indexes(database):
    """Create geospatial indexes on the coordinates field for efficient spatial queries"""
    
    for collection_name in COLLECTIONS:
        collection = database[collection_name]
        
        try:
            start_time = time.time()
            
            # Create 2dsphere index for GeoJSON coordinates
            collection.create_index([("coordinates", "2dsphere")])
            
            # Create compound indexes for common queries
            if collection_name == 'crop_production_data':
                # Index for year + coordinates queries
                collection.create_index([("year", 1), ("coordinates", "2dsphere")])
                # Index for state + coordinates queries  
                collection.create_index([("state", 1), ("coordinates", "2dsphere")])
            
            elif collection_name in ['max_temperature_data', 'min_temperature_data', 'precipitation_data']:
                # Index for year + coordinates queries for climate data
                collection.create_index([("year", 1), ("coordinates", "2dsphere")])
            
            elapsed = time.time() - start_time
            logging.info(f"Created geospatial indexes on {collection_name} (took {elapsed:.1f}s)")
            
        except pymongo.errors.OperationFailure as e:
            if "already exists" in str(e):
                logging.info(f"Indexes already exist on {collection_name}")
            else:
                logging.warning(f"Failed to create indexes on {collection_name}: {e}")
        except Exception as e:
            logging.warning(f"Failed to create indexes on {collection_name}: {e}")

def update_collections_with_coordinates_parallel(database, coordinates_map: Dict[str, Tuple[float, float]]):
    """Update collections with coordinates using parallel processing (alternative method)"""
    import concurrent.futures
    import threading
    
    def update_single_collection(collection_name):
        """Update a single collection - designed to run in parallel"""
        # Create a new connection for this thread
        thread_connection = pymongo.MongoClient(os.getenv("MONGO_URL"))
        thread_database = thread_connection['agriculture_data']
        collection = thread_database[collection_name]
        
        logging.info(f"[{threading.current_thread().name}] Starting {collection_name}")
        start_time = time.time()
        total_docs = collection.count_documents({})
        updated_count = 0
        
        batch_size = 1000
        skip = 0
        
        while skip < total_docs:
            documents = list(collection.find(
                {},
                {"_id": 1, "district": 1, "state": 1}
            ).skip(skip).limit(batch_size))
            
            if not documents:
                break
            
            bulk_operations = []
            
            for doc in documents:
                district = doc.get('district')
                state = doc.get('state')
                
                if district and state:
                    key = f"{district.lower().strip()}, {state.lower().strip()}"
                    
                    if key in coordinates_map:
                        lat, lon = coordinates_map[key]
                        
                        bulk_operations.append(
                            pymongo.UpdateOne(
                                {'_id': doc['_id']},
                                {
                                    '$set': {
                                        'latitude': lat,
                                        'longitude': lon,
                                        'coordinates': [lon, lat]
                                    }
                                }
                            )
                        )
            
            if bulk_operations:
                try:
                    result = collection.bulk_write(bulk_operations, ordered=False)
                    updated_count += result.modified_count
                except Exception as e:
                    logging.error(f"Error in {collection_name}: {e}")
            
            skip += batch_size
            
            if skip % 5000 == 0:
                elapsed = time.time() - start_time
                docs_per_sec = skip / elapsed if elapsed > 0 else 0
                logging.info(f"[{threading.current_thread().name}] {collection_name}: "
                           f"{min(skip, total_docs)}/{total_docs} ({docs_per_sec:.0f} docs/sec)")
        
        elapsed = time.time() - start_time
        logging.info(f"[{threading.current_thread().name}] Completed {collection_name}: "
                   f"{updated_count} updates in {elapsed:.1f}s")
        
        thread_connection.close()
        return updated_count
    
    # Run updates in parallel
    logging.info("Starting parallel collection updates...")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(COLLECTIONS)) as executor:
        future_to_collection = {
            executor.submit(update_single_collection, collection_name): collection_name
            for collection_name in COLLECTIONS
        }
        
        total_updated = 0
        for future in concurrent.futures.as_completed(future_to_collection):
            collection_name = future_to_collection[future]
            try:
                updated_count = future.result()
                total_updated += updated_count
                logging.info(f"✓ Completed {collection_name}: {updated_count} documents updated")
            except Exception as e:
                logging.error(f"✗ Failed {collection_name}: {e}")
    
    elapsed = time.time() - start_time
    logging.info(f"Parallel updates completed: {total_updated} total updates in {elapsed:.1f}s "
               f"({total_updated/elapsed:.0f} updates/sec overall)")

def main():
    logging.info("Starting geocoding process...")
    
    # Check available geocoding services
    has_google_api_key = bool(os.getenv("GOOGLE_MAPS_API_KEY"))
    
    if has_google_api_key:
        logging.info("Google Maps API key found - will use Google Maps as fallback for failed OpenStreetMap requests")
    else:
        logging.info("No Google Maps API key found - using only OpenStreetMap (consider adding GOOGLE_MAPS_API_KEY to .env for better coverage)")
    
    # Initialize cache
    cache = GeocodeCache()
    
    # Get all unique locations
    logging.info("Getting unique district-state combinations...")
    unique_locations = get_unique_locations(database)
    logging.info(f"Found {len(unique_locations)} unique locations to geocode")
    
    # Geocode all unique locations with fallback
    coordinates_map = {}
    failed_locations = []
    fallback_successes = 0
    
    geocoding_start = time.time()
    
    for i, (key, (district, state)) in enumerate(unique_locations.items(), 1):
        logging.info(f"Geocoding {i}/{len(unique_locations)}: {district}, {state}")
        
        # Try geocoding with automatic fallback
        coordinates = geocode_location(district, state, cache, use_google_maps_first=False)
        
        if coordinates:
            coordinates_map[key] = coordinates
        else:
            failed_locations.append((district, state))
            logging.warning(f"All geocoding services failed for: {district}, {state}")
    
    geocoding_elapsed = time.time() - geocoding_start
    
    logging.info(f"Geocoding completed in {geocoding_elapsed:.1f}s")
    logging.info(f"Successfully geocoded {len(coordinates_map)}/{len(unique_locations)} locations")
    logging.info(f"Failed to geocode {len(failed_locations)} locations")
    
    if failed_locations:
        logging.info("Locations that could not be geocoded by any service:")
        for district, state in failed_locations:
            logging.info(f"  - {district}, {state}")
        
        # Save failed locations to a file for manual review
        try:
            with open('failed_geocoding.txt', 'w') as f:
                f.write("Districts that could not be geocoded:\n")
                f.write("Format: District, State\n")
                f.write("-" * 40 + "\n")
                for district, state in failed_locations:
                    f.write(f"{district}, {state}\n")
            logging.info("Failed locations saved to 'failed_geocoding.txt' for manual review")
        except Exception as e:
            logging.warning(f"Could not save failed locations to file: {e}")
    
    # Update all collections with coordinates
    if coordinates_map:
        logging.info("=" * 50)
        logging.info("STARTING DATABASE UPDATES")
        logging.info("=" * 50)
        
        # Choose update method based on collection count
        update_start = time.time()
        

        logging.info("Using parallel update method...")
        update_collections_with_coordinates_parallel(database, coordinates_map)
        
        update_elapsed = time.time() - update_start
        logging.info(f"Database updates completed in {update_elapsed:.1f}s")
        
        # Create geospatial indexes
        logging.info("Creating geospatial indexes...")
        index_start = time.time()
        create_geospatial_indexes(database)
        index_elapsed = time.time() - index_start
        logging.info(f"Index creation completed in {index_elapsed:.1f}s")
        
        # Print summary statistics
        total_elapsed = time.time() - geocoding_start
        logging.info("=" * 50)
        logging.info("FINAL SUMMARY")
        logging.info("=" * 50)
        logging.info(f"Total processing time: {total_elapsed:.1f}s")
        logging.info(f"  - Geocoding: {geocoding_elapsed:.1f}s")
        logging.info(f"  - Database updates: {update_elapsed:.1f}s") 
        logging.info(f"  - Index creation: {index_elapsed:.1f}s")
        logging.info(f"Total unique locations: {len(unique_locations)}")
        logging.info(f"Successfully geocoded: {len(coordinates_map)}")
        logging.info(f"Failed geocoding: {len(failed_locations)}")
        logging.info(f"Success rate: {len(coordinates_map)/len(unique_locations)*100:.1f}%")
        
        if has_google_api_key:
            logging.info("Fallback system: OpenStreetMap → Google Maps")
        else:
            logging.info("Single service mode: OpenStreetMap only")
    else:
        logging.warning("No coordinates were successfully obtained. Please check your network connection and try again.")
    
    # Save final cache
    cache.save_cache()
    
    logging.info("Geocoding process completed!")
    
    # Close connection
    connection.close()

if __name__ == "__main__":
    main()