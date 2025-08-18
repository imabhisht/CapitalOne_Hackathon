"""
Commodity price tool for accessing agricultural commodity prices from the CEDA API.
"""
import os
import requests
import json
from typing import Dict, List, Optional, Tuple
from ...config import get_logger

# Initialize logger
logger = get_logger(__name__)

# CEDA API configuration
CEDA_API_BASE_URL = "https://api.ceda.ashoka.edu.in/v1"
CEDA_API_KEY = os.getenv("CEDA_API_KEY")

def get_ceda_api_headers() -> Dict[str, str]:
    """Get headers for CEDA API requests"""
    return {
        "Authorization": f"Bearer {CEDA_API_KEY}",
        "Content-Type": "application/json"
    }

def geocode_with_google_maps(district: str, state: str) -> Optional[Tuple[float, float]]:
    """Geocode a district and state using Google Maps API"""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        logger.warning("Google Maps API key not found in environment variables")
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
                        logger.info(f"Google Maps geocoded {district}, {state}: ({lat}, {lon})")
                        return (lat, lon)
                    else:
                        logger.warning(f"Google Maps returned coordinates outside India bounds for {district}, {state}: ({lat}, {lon})")
                elif data['status'] == 'ZERO_RESULTS':
                    logger.debug(f"Google Maps found no results for query: {query}")
                    continue
        except Exception as e:
            logger.warning(f"Google Maps API error for query '{query}': {e}")
            continue
    
    return None

def tool_get_commodity_list() -> Dict:
    """
    Get the list of all commodities from the CEDA Agmarknet platform.
    
    Returns:
        Dict: List of commodities with their IDs and names
    """
    logger.info("Getting commodity list from CEDA API")
    
    if not CEDA_API_KEY:
        logger.error("CEDA_API_KEY not set")
        return {"error": "CEDA API key not configured"}
    
    try:
        url = f"{CEDA_API_BASE_URL}/agmarknet/commodities"
        response = requests.get(url, headers=get_ceda_api_headers(), timeout=30)
        
        if response.status_code == 200:
            raw_data = response.json()
            # Extract the actual data from the response structure
            data = raw_data.get("output", {}).get("data", [])
            
            # Transform to the format our code expects
            commodities = []
            for item in data:
                commodities.append({
                    "id": item.get("commodity_id"),
                    "name": item.get("commodity_name")
                })
            
            logger.info(f"Retrieved {len(commodities)} commodities")
            return {
                "success": True,
                "commodities": commodities
            }
        else:
            logger.error(f"CEDA API error: {response.status_code} - {response.text}")
            return {
                "error": f"CEDA API error: {response.status_code}",
                "status_code": response.status_code,
                "response": response.text
            }
            
    except Exception as e:
        logger.error(f"Error retrieving commodity list: {str(e)}", exc_info=True)
        return {
            "error": f"Error retrieving commodity list: {str(e)}"
        }

def tool_get_geographies() -> Dict:
    """
    Get the list of all states and districts available in the CEDA Agmarknet platform.
    
    Returns:
        Dict: List of geographies (states and districts)
    """
    logger.info("Getting geographies from CEDA API")
    
    if not CEDA_API_KEY:
        logger.error("CEDA_API_KEY not set")
        return {"error": "CEDA API key not configured"}
    
    try:
        url = f"{CEDA_API_BASE_URL}/agmarknet/geographies"
        response = requests.get(url, headers=get_ceda_api_headers(), timeout=30)
        
        if response.status_code == 200:
            raw_data = response.json()
            # Extract the actual data from the response structure
            data = raw_data.get("output", {}).get("data", [])
            
            # Transform the flat list into a hierarchical structure
            geographies = []
            state_dict = {}  # To track states we've already added
            
            for item in data:
                state_id = item.get("census_state_id")
                state_name = item.get("census_state_name")
                district_id = item.get("census_district_id")
                district_name = item.get("census_district_name")
                
                # If this is a new state, add it to our list
                if state_id not in state_dict:
                    state_entry = {
                        "state_id": state_id,
                        "state_name": state_name,
                        "districts": []
                    }
                    geographies.append(state_entry)
                    state_dict[state_id] = state_entry
                
                # Add the district to this state
                if state_dict[state_id] and district_id and district_name:
                    state_dict[state_id]["districts"].append({
                        "district_id": district_id,
                        "district_name": district_name
                    })
            
            geography_count = len(geographies)
            district_count = sum(len(state.get('districts', [])) for state in geographies)
            logger.info(f"Retrieved {geography_count} states with {district_count} districts")
            return {
                "success": True,
                "geographies": geographies
            }
        else:
            logger.error(f"CEDA API error: {response.status_code} - {response.text}")
            return {
                "error": f"CEDA API error: {response.status_code}",
                "status_code": response.status_code,
                "response": response.text
            }
            
    except Exception as e:
        logger.error(f"Error retrieving geographies: {str(e)}", exc_info=True)
        return {
            "error": f"Error retrieving geographies: {str(e)}"
        }

def find_state_and_district_ids(state_name: str, district_name: str) -> Optional[Tuple[int, int]]:
    """
    Find the state and district IDs from the CEDA API based on names.
    Includes fuzzy matching to handle slight variations in names.
    
    Args:
        state_name (str): Name of the state
        district_name (str): Name of the district
        
    Returns:
        Tuple[int, int]: State ID and District ID, or None if not found
    """
    logger.info(f"Finding IDs for state '{state_name}' and district '{district_name}'")
    
    # Get all geographies
    geographies_result = tool_get_geographies()
    if not geographies_result.get("success"):
        logger.error("Failed to get geographies")
        return None
    
    geographies = geographies_result.get("geographies", [])
    
    # Normalize search terms
    state_search = state_name.lower().strip()
    district_search = district_name.lower().strip()
    
    # Remove common suffixes/prefixes for better matching
    district_search = district_search.replace(' district', '').replace(' division', '').replace('district ', '').replace('division ', '')
    
    # Find matching state and district
    for state in geographies:
        # Match state name (case insensitive and fuzzy)
        state_name_from_data = state.get("state_name", "").lower().strip()
        
        # Check exact match or if one contains the other
        state_match = (
            state_name_from_data == state_search or
            state_search in state_name_from_data or
            state_name_from_data in state_search
        )
        
        if state_match:
            state_id = state.get("state_id")
            logger.debug(f"Found matching state: {state.get('state_name')} (ID: {state_id})")
            
            # Look for district in this state
            for district in state.get("districts", []):
                district_name_from_data = district.get("district_name", "").lower().strip()
                
                # Remove common suffixes/prefixes from database name too
                district_clean = district_name_from_data.replace(' district', '').replace(' division', '').replace('district ', '').replace('division ', '')
                
                # Check multiple matching strategies
                district_match = (
                    district_clean == district_search or  # Exact match after cleaning
                    district_search in district_clean or  # Search term in clean district name
                    district_clean in district_search or  # Clean district name in search term
                    district_name_from_data == district_search or  # Exact match original
                    district_search in district_name_from_data or  # Search in original
                    district_name_from_data in district_search     # Original in search
                )
                
                if district_match:
                    district_id = district.get("district_id")
                    logger.info(f"Found matching district: {district.get('district_name')} (ID: {district_id}) in {state.get('state_name')} (ID: {state_id})")
                    return (state_id, district_id)
    
    # If no exact match found, try partial matching
    logger.warning(f"No exact match found. Attempting partial matching...")
    
    for state in geographies:
        state_name_from_data = state.get("state_name", "").lower()
        
        # More lenient state matching
        if any(word in state_name_from_data for word in state_search.split()) or any(word in state_search for word in state_name_from_data.split()):
            state_id = state.get("state_id")
            logger.debug(f"Partial state match: {state.get('state_name')} (ID: {state_id})")
            
            # Look for district with partial matching
            for district in state.get("districts", []):
                district_name_from_data = district.get("district_name", "").lower()
                
                # Check if key words match
                district_words = district_search.split()
                data_words = district_name_from_data.replace(' district', '').replace(' division', '').split()
                
                if any(word in data_words for word in district_words if len(word) > 2):
                    district_id = district.get("district_id")
                    logger.info(f"Found partial matching district: {district.get('district_name')} (ID: {district_id}) in {state.get('state_name')} (ID: {state_id})")
                    return (state_id, district_id)
    
    logger.warning(f"State '{state_name}' or district '{district_name}' not found in CEDA database after fuzzy matching")
    return None

def tool_get_markets_for_commodity(commodity_id: int, state_id: int, district_id: int, indicator: str = "price") -> Dict:
    """
    Get the list of markets for a given commodity, state and district.
    
    Args:
        commodity_id (int): Commodity ID
        state_id (int): State ID
        district_id (int): District ID
        indicator (str): Indicator type ("price" or "quantity")
        
    Returns:
        Dict: List of markets
    """
    logger.info(f"Getting markets for commodity {commodity_id}, state {state_id}, district {district_id}")
    
    if not CEDA_API_KEY:
        logger.error("CEDA_API_KEY not set")
        return {"error": "CEDA API key not configured"}
    
    if indicator not in ["price", "quantity"]:
        logger.error(f"Invalid indicator: {indicator}")
        return {"error": "Invalid indicator. Must be 'price' or 'quantity'"}
    
    try:
        url = f"{CEDA_API_BASE_URL}/agmarknet/markets"
        payload = {
            "commodity_id": commodity_id,
            "state_id": state_id,
            "district_id": district_id,
            "indicator": indicator
        }
        
        response = requests.post(url, headers=get_ceda_api_headers(), json=payload, timeout=30)
        
        if response.status_code == 200:
            raw_data = response.json()
            # Extract the actual data from the response structure
            data = raw_data.get("output", {}).get("data", [])
            
            # Transform to the format our code expects
            markets = []
            for item in data:
                markets.append({
                    "census_state_id": item.get("census_state_id"),
                    "census_district_id": item.get("census_district_id"),
                    "market_id": item.get("market_id"),
                    "market_name": item.get("market_name")
                })
            
            logger.info(f"Retrieved {len(markets)} markets")
            return {
                "success": True,
                "markets": markets
            }
        else:
            logger.error(f"CEDA API error: {response.status_code} - {response.text}")
            return {
                "error": f"CEDA API error: {response.status_code}",
                "status_code": response.status_code,
                "response": response.text
            }
            
    except Exception as e:
        logger.error(f"Error retrieving markets: {str(e)}", exc_info=True)
        return {
            "error": f"Error retrieving markets: {str(e)}"
        }

def tool_get_commodity_prices(
    commodity_id: int, 
    state_id: int, 
    district_ids: Optional[List[int]] = None,
    market_ids: Optional[List[int]] = None,
    from_date: str = "2025-01-01",
    to_date: str = "2025-08-18"
) -> Dict:
    """
    Get the prices for a commodity at the national, state, district or market level.
    
    Args:
        commodity_id (int): Commodity ID
        state_id (int): State ID (use 0 for all India level data)
        district_ids (List[int], optional): District IDs
        market_ids (List[int], optional): Market IDs
        from_date (str): Start date (YYYY-MM-DD)
        to_date (str): End date (YYYY-MM-DD)
        
    Returns:
        Dict: Price data
    """
    logger.info(f"Getting prices for commodity {commodity_id}")
    
    if not CEDA_API_KEY:
        logger.error("CEDA_API_KEY not set")
        return {"error": "CEDA API key not configured"}
    
    try:
        url = f"{CEDA_API_BASE_URL}/agmarknet/prices"
        payload = {
            "commodity_id": commodity_id,
            "state_id": state_id,
            "from_date": from_date,
            "to_date": to_date
        }
        
        if district_ids:
            payload["district_id"] = district_ids
            
        if market_ids:
            payload["market_id"] = market_ids
        
        response = requests.post(url, headers=get_ceda_api_headers(), json=payload, timeout=30)
        
        if response.status_code == 200:
            raw_data = response.json()
            # Extract the actual data from the response structure
            data = raw_data.get("output", {}).get("data", [])
            
            # Transform to the format our code expects
            prices = []
            for item in data:
                prices.append({
                    "date": item.get("date"),
                    "commodity_id": item.get("commodity_id"),
                    "census_state_id": item.get("census_state_id"),
                    "census_district_id": item.get("census_district_id"),
                    "market_id": item.get("market_id"),
                    "min_price": item.get("min_price"),
                    "max_price": item.get("max_price"),
                    "modal_price": item.get("modal_price")
                })
            
            logger.info(f"Retrieved {len(prices)} price records")
            return {
                "success": True,
                "prices": prices,
                "count": len(prices)
            }
        else:
            logger.error(f"CEDA API error: {response.status_code} - {response.text}")
            return {
                "error": f"CEDA API error: {response.status_code}",
                "status_code": response.status_code,
                "response": response.text
            }
            
    except Exception as e:
        logger.error(f"Error retrieving prices: {str(e)}", exc_info=True)
        return {
            "error": f"Error retrieving prices: {str(e)}"
        }

def tool_get_commodity_quantities(
    commodity_id: int, 
    state_id: int, 
    district_ids: Optional[List[int]] = None,
    market_ids: Optional[List[int]] = None,
    from_date: str = "2025-01-01",
    to_date: str = "2025-08-18"
) -> Dict:
    """
    Get the quantities for a commodity at the national, state, district or market level.
    
    Args:
        commodity_id (int): Commodity ID
        state_id (int): State ID (use 0 for all India level data)
        district_ids (List[int], optional): District IDs
        market_ids (List[int], optional): Market IDs
        from_date (str): Start date (YYYY-MM-DD)
        to_date (str): End date (YYYY-MM-DD)
        
    Returns:
        Dict: Quantity data
    """
    logger.info(f"Getting quantities for commodity {commodity_id}")
    
    if not CEDA_API_KEY:
        logger.error("CEDA_API_KEY not set")
        return {"error": "CEDA API key not configured"}
    
    try:
        url = f"{CEDA_API_BASE_URL}/agmarknet/quantities"
        payload = {
            "commodity_id": commodity_id,
            "state_id": state_id,
            "from_date": from_date,
            "to_date": to_date
        }
        
        if district_ids:
            payload["district_id"] = district_ids
            
        if market_ids:
            payload["market_id"] = market_ids
        
        response = requests.post(url, headers=get_ceda_api_headers(), json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Retrieved {len(data.get('data', []))} quantity records")
            return {
                "success": True,
                "quantities": data.get("data", []),
                "count": len(data.get("data", []))
            }
        else:
            logger.error(f"CEDA API error: {response.status_code} - {response.text}")
            return {
                "error": f"CEDA API error: {response.status_code}",
                "status_code": response.status_code,
                "response": response.text
            }
            
    except Exception as e:
        logger.error(f"Error retrieving quantities: {str(e)}", exc_info=True)
        return {
            "error": f"Error retrieving quantities: {str(e)}"
        }

def tool_get_commodity_prices_by_location(
    lat: float, 
    lon: float, 
    commodity_name: str,
    from_date: str = "2025-01-01",
    to_date: str = "2025-08-18"
) -> Dict:
    """
    Get commodity prices for the nearest district/state based on latitude and longitude.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        commodity_name (str): Name of the commodity
        from_date (str): Start date (YYYY-MM-DD)
        to_date (str): End date (YYYY-MM-DD)
        
    Returns:
        Dict: Price data for the commodity in the nearest district
    """
    logger.info(f"Getting prices for {commodity_name} near coordinates {lat}, {lon}")
    
    if not CEDA_API_KEY:
        logger.error("CEDA_API_KEY not set")
        return {"error": "CEDA API key not configured"}
    
    # First, we need to find the district/state for the given coordinates
    # This would typically involve using a reverse geocoding service or a database lookup
    # For now, we'll return an error indicating this functionality needs implementation
    logger.warning("Reverse geocoding for district/state not yet implemented")
    return {
        "error": "Reverse geocoding for district/state not yet implemented. Please provide district and state directly.",
        "suggestion": "Use the get_geographies tool to find available states and districts, then use get_commodity_prices with specific state and district IDs."
    }

def tool_get_commodity_price_by_name_and_location(
    commodity_name: str,
    state_name: str,
    district_name: str,
    from_date: str = "2025-07-18",
    to_date: str = "2025-08-18"
) -> Dict:
    """
    Get commodity prices by commodity name and location names (state and district).
    This implements the full workflow:
    1. Find commodity ID by name
    2. Find state and district IDs by names
    3. Get markets for the commodity in that location
    4. Get prices for those markets
    
    Args:
        commodity_name (str): Name of the commodity
        state_name (str): Name of the state
        district_name (str): Name of the district
        from_date (str): Start date (YYYY-MM-DD)
        to_date (str): End date (YYYY-MM-DD)
        
    Returns:
        Dict: Price data for the commodity in the specified location
    """
    logger.info(f"Getting prices for {commodity_name} in {district_name}, {state_name}")
    
    if not CEDA_API_KEY:
        logger.error("CEDA_API_KEY not set")
        return {"error": "CEDA API key not configured"}
    
    try:
        # Step 1: Find commodity ID by name
        logger.debug("Step 1: Finding commodity ID")
        commodities_result = tool_get_commodity_list()
        if not commodities_result.get("success"):
            return commodities_result
        
        commodity_id = None
        for commodity in commodities_result.get("commodities", []):
            if commodity.get("name", "").lower() == commodity_name.lower():
                commodity_id = commodity.get("id")
                break
        
        if commodity_id is None:
            available_commodities = [c.get("name") for c in commodities_result.get("commodities", [])]
            logger.warning(f"Commodity '{commodity_name}' not found. Available commodities: {available_commodities[:10]}...")
            return {
                "error": f"Commodity '{commodity_name}' not found in CEDA database",
                "available_commodities": available_commodities[:10]  # Show first 10
            }
        
        logger.info(f"Found commodity ID {commodity_id} for '{commodity_name}'")
        
        # Step 2: Find state and district IDs
        logger.debug("Step 2: Finding state and district IDs")
        ids = find_state_and_district_ids(state_name, district_name)
        if ids is None:
            return {
                "error": f"State '{state_name}' or district '{district_name}' not found in CEDA database",
                "suggestion": "Check the spelling of state and district names"
            }
        
        state_id, district_id = ids
        logger.info(f"Found state ID {state_id} and district ID {district_id}")
        
        # Step 3: Get markets for the commodity in that location
        logger.debug("Step 3: Getting markets")
        markets_result = tool_get_markets_for_commodity(commodity_id, state_id, district_id, "price")
        if not markets_result.get("success"):
            return markets_result
        
        markets = markets_result.get("markets", [])
        if not markets:
            return {
                "error": f"No markets found for {commodity_name} in {district_name}, {state_name}",
                "suggestion": "Try a different commodity or location"
            }
        
        logger.info(f"Found {len(markets)} markets")
        
        # Get market IDs
        market_ids = [market.get("market_id") for market in markets]
        
        # Step 4: Get prices for those markets
        logger.debug("Step 4: Getting prices")
        prices_result = tool_get_commodity_prices(
            commodity_id, 
            state_id, 
            district_ids=[district_id], 
            market_ids=market_ids,
            from_date=from_date,
            to_date=to_date
        )
        
        if not prices_result.get("success"):
            return prices_result
        
        prices = prices_result.get("prices", [])
        
        # Format the response with market names and price information
        formatted_prices = []
        market_names = {market.get("market_id"): market.get("market_name") for market in markets}
        
        for price in prices:
            market_id = price.get("market_id")
            formatted_prices.append({
                "date": price.get("date"),
                "market": market_names.get(market_id, f"Market ID {market_id}"),
                "min_price": price.get("min_price"),
                "max_price": price.get("max_price"),
                "modal_price": price.get("modal_price"),
                "unit": "₹/Quintal"  # Assuming prices are in Rupees per Quintal
            })
        
        return {
            "success": True,
            "commodity": commodity_name,
            "location": {
                "state": state_name,
                "district": district_name
            },
            "date_range": {
                "from": from_date,
                "to": to_date
            },
            "prices": formatted_prices,
            "count": len(formatted_prices)
        }
        
    except Exception as e:
        logger.error(f"Error in tool_get_commodity_price_by_name_and_location: {str(e)}", exc_info=True)
        return {
            "error": f"Error retrieving commodity prices: {str(e)}"
        }

def reverse_geocode_with_google_maps(lat: float, lon: float) -> Optional[Tuple[str, str]]:
    """
    Reverse geocode latitude and longitude to get state and district using Google Maps API
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        
    Returns:
        Tuple[str, str]: State name and district name, or None if not found
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        logger.warning("Google Maps API key not found in environment variables")
        return None
    
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'latlng': f"{lat},{lon}",
            'key': api_key,
            'result_type': 'administrative_area_level_1|administrative_area_level_2|locality',  # State, district, and city
            'language': 'en'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                state_name = None
                district_name = None
                locality_name = None
                
                for result in data['results']:
                    for component in result.get('address_components', []):
                        types = component.get('types', [])
                        
                        # Get state name
                        if 'administrative_area_level_1' in types:
                            state_name = component.get('long_name')
                        
                        # Get district name
                        if 'administrative_area_level_2' in types:
                            district_name = component.get('long_name')
                        
                        # Get locality/city name as backup
                        if 'locality' in types and not district_name:
                            locality_name = component.get('long_name')
                
                # Clean up district name
                if district_name:
                    # Remove common suffixes
                    for suffix in [' District', ' Division', ' district', ' division']:
                        if district_name.endswith(suffix):
                            district_name = district_name.replace(suffix, '')
                            break
                
                # If no district but we have locality, use locality
                if not district_name and locality_name:
                    district_name = locality_name
                    logger.debug(f"Using locality '{locality_name}' as district name")
                
                if state_name and district_name:
                    logger.info(f"Reverse geocoded ({lat}, {lon}) to {district_name}, {state_name}")
                    return (state_name, district_name)
                else:
                    logger.warning(f"Could not extract both state and district from reverse geocoding for ({lat}, {lon}). State: {state_name}, District: {district_name}")
            else:
                logger.warning(f"Google Maps reverse geocoding failed for ({lat}, {lon}): {data.get('status')}")
                
    except Exception as e:
        logger.error(f"Error in reverse geocoding ({lat}, {lon}): {e}")
    
    return None

def tool_get_commodity_price_by_location_and_name(
    commodity_name: str,
    lat: float,
    lon: float,
    from_date: str = "2025-07-18",
    to_date: str = "2025-08-18"
) -> Dict:
    """
    Get commodity prices by commodity name and coordinates.
    This implements the complete enhanced workflow:
    1. Reverse geocode coordinates to get state and district names
    2. Find commodity ID by name
    3. Find state and district IDs by names
    4. Get markets for the commodity in that location
    5. Get prices for those markets
    
    Args:
        commodity_name (str): Name of the commodity
        lat (float): Latitude
        lon (float): Longitude
        from_date (str): Start date (YYYY-MM-DD)
        to_date (str): End date (YYYY-MM-DD)
        
    Returns:
        Dict: Price data for the commodity in the detected location
    """
    logger.info(f"Getting prices for {commodity_name} near coordinates ({lat}, {lon})")
    
    if not CEDA_API_KEY:
        logger.error("CEDA_API_KEY not set")
        return {"error": "CEDA API key not configured"}
    
    try:
        # Step 1: Reverse geocode to get state and district
        logger.debug("Step 1: Reverse geocoding coordinates to location")
        location_result = reverse_geocode_with_google_maps(lat, lon)
        
        if location_result is None:
            return {
                "error": "Could not determine state and district from coordinates",
                "suggestion": "Please provide state and district names directly"
            }
        
        state_name, district_name = location_result
        logger.info(f"Detected location: {district_name}, {state_name}")
        
        # Step 2: Use the existing workflow with the detected location
        logger.debug("Step 2: Getting commodity prices for detected location")
        result = tool_get_commodity_price_by_name_and_location(
            commodity_name=commodity_name,
            state_name=state_name,
            district_name=district_name,
            from_date=from_date,
            to_date=to_date
        )
        
        # Add coordinate information to the response
        if result.get("success"):
            result["coordinates"] = {
                "latitude": lat,
                "longitude": lon
            }
            result["location_method"] = "reverse_geocoded"
        
        return result
        
    except Exception as e:
        logger.error(f"Error in tool_get_commodity_price_by_location_and_name: {str(e)}", exc_info=True)
        return {
            "error": f"Error retrieving commodity prices by location: {str(e)}"
        }

def tool_intelligent_commodity_price_query(
    query: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    user_location: Optional[str] = None
) -> Dict:
    """
    Intelligent commodity price query that can handle various types of user requests.
    This function uses LLM-like intelligence to parse the user query and extract:
    - Commodity name
    - Location (from coordinates, user location, or query text)
    - Date range (if mentioned)
    
    Args:
        query (str): User's natural language query about commodity prices
        lat (float, optional): User's latitude
        lon (float, optional): User's longitude  
        user_location (str, optional): User's location as text
        
    Returns:
        Dict: Price data for the commodity based on the intelligent query parsing
    """
    logger.info(f"Processing intelligent commodity query: {query}")
    
    # Common commodity mappings
    commodity_aliases = {
        'cotton': 'Cotton',
        'rice': 'Rice',
        'wheat': 'Wheat',
        'maize': 'Maize',
        'sugarcane': 'Sugarcane',
        'onion': 'Onion',
        'potato': 'Potato',
        'tomato': 'Tomato',
        'soybean': 'Soybean',
        'groundnut': 'Groundnut',
        'mustard': 'Mustard',
        'turmeric': 'Turmeric',
        'chilli': 'Chilli',
        'pepper': 'Black pepper',
        'cardamom': 'Cardamom',
        'ginger': 'Ginger',
        'garlic': 'Garlic',
        'coconut': 'Coconut',
        'areca nut': 'Arecanut',
        'coffee': 'Coffee',
        'tea': 'Tea'
    }
    
    # State and district mappings
    state_aliases = {
        'mh': 'Maharashtra',
        'maharashtra': 'Maharashtra',
        'ap': 'Andhra Pradesh',
        'andhra pradesh': 'Andhra Pradesh',
        'tn': 'Tamil Nadu',
        'tamil nadu': 'Tamil Nadu',
        'karnataka': 'Karnataka',
        'kn': 'Karnataka',
        'gujarat': 'Gujarat',
        'gj': 'Gujarat',
        'rajasthan': 'Rajasthan',
        'rj': 'Rajasthan',
        'mp': 'Madhya Pradesh',
        'madhya pradesh': 'Madhya Pradesh',
        'up': 'Uttar Pradesh',
        'uttar pradesh': 'Uttar Pradesh',
        'punjab': 'Punjab',
        'pb': 'Punjab',
        'haryana': 'Haryana',
        'hr': 'Haryana',
        'wb': 'West Bengal',
        'west bengal': 'West Bengal',
        'odisha': 'Odisha',
        'or': 'Odisha',
        'telangana': 'Telangana',
        'ts': 'Telangana',
        'kerala': 'Kerala',
        'kl': 'Kerala'
    }
    
    try:
        query_lower = query.lower()
        
        # Extract commodity name
        commodity_name = None
        for alias, full_name in commodity_aliases.items():
            if alias in query_lower:
                commodity_name = full_name
                break
        
        if commodity_name is None:
            return {
                "error": "Could not identify commodity from the query",
                "suggestion": f"Please mention one of these commodities: {', '.join(list(commodity_aliases.keys())[:10])}..."
            }
        
        logger.info(f"Detected commodity: {commodity_name}")
        
        # Extract location information
        state_name = None
        district_name = None
        
        # Check if location is provided in query text
        for alias, full_name in state_aliases.items():
            if alias in query_lower:
                state_name = full_name
                break
        
        # If we have coordinates, use them
        if lat is not None and lon is not None:
            logger.debug("Using provided coordinates for location detection")
            return tool_get_commodity_price_by_location_and_name(
                commodity_name=commodity_name,
                lat=lat,
                lon=lon
            )
        
        # If we have user location text, try to parse it
        if user_location:
            location_parts = user_location.split(',')
            if len(location_parts) >= 2:
                district_name = location_parts[0].strip()
                state_name = location_parts[1].strip()
                
                # Normalize state name
                state_name_lower = state_name.lower()
                if state_name_lower in state_aliases:
                    state_name = state_aliases[state_name_lower]
        
        # If we detected state from query but not district, we need both
        if state_name and not district_name:
            return {
                "error": f"Please specify the district within {state_name}",
                "suggestion": f"Try asking: 'What is the price of {commodity_name.lower()} in [district name], {state_name}?'"
            }
        
        # If we don't have location info
        if not state_name or not district_name:
            return {
                "error": "Could not determine location from the query",
                "suggestion": "Please provide either coordinates or specify state and district names like 'price of cotton in Nagpur, Maharashtra'"
            }
        
        logger.info(f"Detected location: {district_name}, {state_name}")
        
        # Use the existing workflow with detected information
        return tool_get_commodity_price_by_name_and_location(
            commodity_name=commodity_name,
            state_name=state_name,
            district_name=district_name
        )
        
    except Exception as e:
        logger.error(f"Error in tool_intelligent_commodity_price_query: {str(e)}", exc_info=True)
        return {
            "error": f"Error processing commodity price query: {str(e)}"
        }