"""
API call logic for OpenRouter and tool call handling.
"""
import os
import json
from openai import OpenAI
from typing import List, Dict, Optional
from dotenv import load_dotenv
from .tools import (
    tool_get_weather_by_coords, 
    tool_get_lat_lon_from_browser, 
    tool_get_date_time, 
    tool_get_crop_data_by_location, 
    tool_get_irrigation_data_by_location, 
    tool_get_climate_data_by_location, 
    tool_get_commodity_list, 
    tool_get_geographies, 
    tool_get_markets_for_commodity, 
    tool_get_commodity_prices, 
    tool_get_commodity_quantities, 
    tool_get_commodity_prices_by_location, 
    tool_get_commodity_price_by_name_and_location,
    tool_get_commodity_price_by_location_and_name,
    tool_intelligent_commodity_price_query
)
from ..config import get_logger
from .ui.formatting import format_agricultural_data

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")
APP_TITLE = "Smart Location-Aware Assistant"

def openrouter_tools_schema() -> List[Dict]:
    logger.debug("Generating OpenRouter tools schema")
    schema = [
        {
            "type": "function",
            "function": {
                "name": "get_weather_by_coords",
                "description": "Get comprehensive current weather information by latitude and longitude.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lat": {"type": "number", "description": "Latitude in decimal degrees", "minimum": -90, "maximum": 90},
                        "lon": {"type": "number", "description": "Longitude in decimal degrees", "minimum": -180, "maximum": 180}
                    },
                    "required": ["lat", "lon"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_lat_lon_from_browser",
                "description": "Get the user's current coordinates from their browser geolocation.",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_date_time",
                "description": "Get the current date and time in the user's timezone.",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_crop_data_by_location",
                "description": "Get crop production data for the nearest location within 200 kilometers based on latitude and longitude.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lat": {"type": "number", "description": "Latitude in decimal degrees", "minimum": -90, "maximum": 90},
                        "lon": {"type": "number", "description": "Longitude in decimal degrees", "minimum": -180, "maximum": 180},
                        "year": {"type": "integer", "description": "Specific year to query (optional)"}
                    },
                    "required": ["lat", "lon"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_irrigation_data_by_location",
                "description": "Get irrigation source data for the nearest location within 200 kilometers based on latitude and longitude.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lat": {"type": "number", "description": "Latitude in decimal degrees", "minimum": -90, "maximum": 90},
                        "lon": {"type": "number", "description": "Longitude in decimal degrees", "minimum": -180, "maximum": 180},
                        "year": {"type": "integer", "description": "Specific year to query (optional)"}
                    },
                    "required": ["lat", "lon"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_climate_data_by_location",
                "description": "Get climate data (temperature or precipitation) for the nearest location within 200 kilometers based on latitude and longitude.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lat": {"type": "number", "description": "Latitude in decimal degrees", "minimum": -90, "maximum": 90},
                        "lon": {"type": "number", "description": "Longitude in decimal degrees", "minimum": -180, "maximum": 180},
                        "data_type": {"type": "string", "description": "Type of climate data ('temperature' or 'precipitation')", "enum": ["temperature", "precipitation"]},
                        "year": {"type": "integer", "description": "Specific year to query (optional)"}
                    },
                    "required": ["lat", "lon", "data_type"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_commodity_list",
                "description": "Get the list of all agricultural commodities available in the CEDA Agmarknet database.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_geographies",
                "description": "Get the list of all states and districts available in the CEDA Agmarknet database.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_markets_for_commodity",
                "description": "Get the list of markets for a given commodity, state and district.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "commodity_id": {"type": "integer", "description": "Commodity ID (required). Get from get_commodity_list."},
                        "state_id": {"type": "integer", "description": "State ID (required). Get from get_geographies."},
                        "district_id": {"type": "integer", "description": "District ID (required). Get from get_geographies."},
                        "indicator": {"type": "string", "description": "Indicator type (required, must be 'price' or 'quantity')", "enum": ["price", "quantity"]}
                    },
                    "required": ["commodity_id", "state_id", "district_id", "indicator"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_commodity_prices",
                "description": "Get the prices for a commodity at the state, district or market level.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "commodity_id": {"type": "integer", "description": "Commodity ID (required)"},
                        "state_id": {"type": "integer", "description": "State ID (required). Use 0 for all India level data or state level integer value obtained from get_geographies."},
                        "district_id": {"type": "array", "items": {"type": "integer"}, "description": "Optional district IDs. If not provided, will fetch data at the state level."},
                        "market_id": {"type": "array", "items": {"type": "integer"}, "description": "Optional market IDs. If not provided, will fetch data at the district level."},
                        "from_date": {"type": "string", "format": "date", "description": "Start date (required, format: YYYY-MM-DD)"},
                        "to_date": {"type": "string", "format": "date", "description": "End date (required, format: YYYY-MM-DD)"}
                    },
                    "required": ["commodity_id", "state_id", "from_date", "to_date"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_commodity_quantities",
                "description": "Get the quantities for a commodity at the state, district or market level.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "commodity_id": {"type": "integer", "description": "Commodity ID (required)"},
                        "state_id": {"type": "integer", "description": "State ID (required). Use 0 for all India level data or state level integer value obtained from get_geographies."},
                        "district_id": {"type": "array", "items": {"type": "integer"}, "description": "Optional district IDs. If not provided, will fetch data at the state level."},
                        "market_id": {"type": "array", "items": {"type": "integer"}, "description": "Optional market IDs. If not provided, will fetch data at the district level."},
                        "from_date": {"type": "string", "format": "date", "description": "Start date (required, format: YYYY-MM-DD)"},
                        "to_date": {"type": "string", "format": "date", "description": "End date (required, format: YYYY-MM-DD)"}
                    },
                    "required": ["commodity_id", "state_id", "from_date", "to_date"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_commodity_price_by_name_and_location",
                "description": "Get commodity prices by commodity name and location names (state and district). This tool handles the full workflow of finding IDs and getting prices.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "commodity_name": {"type": "string", "description": "Name of the commodity (e.g., 'Cotton', 'Rice')"},
                        "state_name": {"type": "string", "description": "Name of the state (e.g., 'Maharashtra', 'Andhra Pradesh')"},
                        "district_name": {"type": "string", "description": "Name of the district (e.g., 'Nagpur', 'Anantapur')"},
                        "from_date": {"type": "string", "format": "date", "description": "Start date (required, format: YYYY-MM-DD, default: 30 days ago)"},
                        "to_date": {"type": "string", "format": "date", "description": "End date (required, format: YYYY-MM-DD, default: today)"}
                    },
                    "required": ["commodity_name", "state_name", "district_name"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_commodity_price_by_location_and_name",
                "description": "Get commodity prices by commodity name and coordinates. Uses reverse geocoding to determine state and district, then gets commodity prices.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "commodity_name": {"type": "string", "description": "Name of the commodity (e.g., 'Cotton', 'Rice')"},
                        "lat": {"type": "number", "description": "Latitude in decimal degrees", "minimum": -90, "maximum": 90},
                        "lon": {"type": "number", "description": "Longitude in decimal degrees", "minimum": -180, "maximum": 180},
                        "from_date": {"type": "string", "format": "date", "description": "Start date (optional, format: YYYY-MM-DD, default: 30 days ago)"},
                        "to_date": {"type": "string", "format": "date", "description": "End date (optional, format: YYYY-MM-DD, default: today)"}
                    },
                    "required": ["commodity_name", "lat", "lon"],
                    "additionalProperties": False
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "intelligent_commodity_price_query",
                "description": "Intelligent commodity price query that can handle natural language requests. Automatically extracts commodity name and location from user queries.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "User's natural language query about commodity prices (e.g., 'What is the price of cotton in Maharashtra?')"},
                        "lat": {"type": "number", "description": "User's latitude (optional)", "minimum": -90, "maximum": 90},
                        "lon": {"type": "number", "description": "User's longitude (optional)", "minimum": -180, "maximum": 180},
                        "user_location": {"type": "string", "description": "User's location as text (optional, e.g., 'Nagpur, Maharashtra')"}
                    },
                    "required": ["query"],
                    "additionalProperties": False
                }
            }
        }
    ]
    logger.debug(f"Generated {len(schema)} tool schemas")
    return schema

def call_openrouter_chat(messages: List[Dict], system_prompt: Optional[str] = None, tools: Optional[List[Dict]] = None, tool_choice: Optional[str] = "auto", temperature: float = 0.7, max_tokens: Optional[int] = None) -> Dict:
    logger.debug(f"Starting OpenRouter API call with {len(messages)} messages")
    logger.debug(f"System prompt length: {len(system_prompt) if system_prompt else 0}")
    logger.debug(f"Tools available: {len(tools) if tools else 0}")
    logger.debug(f"Tool choice: {tool_choice}, Temperature: {temperature}, Max tokens: {max_tokens}")
    
    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY is not set")
        raise RuntimeError("OPENROUTER_API_KEY is not set. Please add it to your .env file.")
    
    client = OpenAI(base_url=OPENROUTER_API_BASE, api_key=OPENROUTER_API_KEY)
    headers = {"HTTP-Referer": "http://localhost:8501/", "X-Title": APP_TITLE}
    
    message_payload = []
    if system_prompt:
        message_payload.append({"role": "system", "content": system_prompt})
        logger.debug("Added system prompt to payload")
    message_payload.extend(messages)
    
    payload = {"model": OPENROUTER_MODEL, "messages": message_payload, "temperature": temperature}
    if max_tokens:
        payload["max_tokens"] = max_tokens
    if tools:
        payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
    
    try:
        logger.info(f"Making API call to OpenRouter with model: {OPENROUTER_MODEL}")
        completion = client.chat.completions.create(extra_headers=headers, extra_body={}, **payload)
        response = json.loads(completion.model_dump_json())
        
        # Log response details
        choices = response.get("choices", [])
        if choices:
            choice = choices[0]
            message = choice.get("message", {})
            content_length = len(message.get("content", "")) if message.get("content") else 0
            tool_calls = message.get("tool_calls") or []
            logger.info(f"API response received - Content length: {content_length}, Tool calls: {len(tool_calls)}")
            
            if tool_calls:
                tool_names = [tc.get("function", {}).get("name", "unknown") for tc in tool_calls]
                logger.debug(f"Tool calls requested: {tool_names}")
        
        return response
    except Exception as e:
        logger.error(f"OpenRouter API call failed: {str(e)}", exc_info=True)
        return {"error": f"OpenRouter API call failed: {str(e)}"}

def handle_tool_calls(choice: Dict) -> List[Dict]:
    logger.debug("Starting tool call handling")
    tool_msgs: List[Dict] = []
    message = choice.get("message", {})
    tool_calls = message.get("tool_calls") or []
    
    logger.info(f"Processing {len(tool_calls)} tool calls")
    
    for i, tc in enumerate(tool_calls):
        fn = tc.get("function", {})
        name = fn.get("name")
        args_raw = fn.get("arguments")
        tool_call_id = tc.get("id")
        
        logger.debug(f"Processing tool call {i+1}/{len(tool_calls)}: {name}")
        logger.debug(f"Tool call ID: {tool_call_id}")
        logger.debug(f"Raw arguments: {args_raw}")
        
        try:
            args = json.loads(args_raw) if isinstance(args_raw, str) else (args_raw or {})
            logger.debug(f"Parsed arguments: {args}")
        except Exception as e:
            logger.error(f"Failed to parse tool arguments for {name}: {str(e)}")
            result = {"error": f"Invalid JSON arguments: {str(e)}"}
        else:
            try:
                logger.info(f"Executing tool: {name}")
                if name == "get_weather_by_coords":
                    lat = args.get("lat")
                    lon = args.get("lon")
                    if lat is None or lon is None:
                        logger.error(f"Missing coordinates for weather tool - lat: {lat}, lon: {lon}")
                        result = {"error": "Both lat and lon parameters are required"}
                    else:
                        logger.debug(f"Getting weather for coordinates: {lat}, {lon}")
                        result = tool_get_weather_by_coords(float(lat), float(lon))
                        
                elif name == "get_lat_lon_from_browser":
                    logger.debug("Getting browser location")
                    result = tool_get_lat_lon_from_browser()
                    
                elif name == "get_date_time":
                    logger.debug("Getting current date/time")
                    result = tool_get_date_time()
                    
                elif name == "get_crop_data_by_location":
                    lat = args.get("lat")
                    lon = args.get("lon")
                    year = args.get("year")
                    if lat is None or lon is None:
                        logger.error(f"Missing coordinates for crop data tool - lat: {lat}, lon: {lon}")
                        result = {"error": "Both lat and lon parameters are required"}
                    else:
                        logger.debug(f"Getting crop data for coordinates: {lat}, {lon}" + (f" for year {year}" if year else ""))
                        result = tool_get_crop_data_by_location(float(lat), float(lon), year)
                        # Format the result for better display
                        if isinstance(result, dict) and (result.get("success") or result.get("error")):
                            formatted_result = format_agricultural_data(result)
                            result = {"formatted_response": formatted_result, "raw_data": result}
                        
                elif name == "get_irrigation_data_by_location":
                    lat = args.get("lat")
                    lon = args.get("lon")
                    year = args.get("year")
                    if lat is None or lon is None:
                        logger.error(f"Missing coordinates for irrigation data tool - lat: {lat}, lon: {lon}")
                        result = {"error": "Both lat and lon parameters are required"}
                    else:
                        logger.debug(f"Getting irrigation data for coordinates: {lat}, {lon}" + (f" for year {year}" if year else ""))
                        result = tool_get_irrigation_data_by_location(float(lat), float(lon), year)
                        # Format the result for better display
                        if isinstance(result, dict) and (result.get("success") or result.get("error")):
                            formatted_result = format_agricultural_data(result)
                            result = {"formatted_response": formatted_result, "raw_data": result}
                        
                elif name == "get_climate_data_by_location":
                    lat = args.get("lat")
                    lon = args.get("lon")
                    data_type = args.get("data_type")
                    year = args.get("year")
                    if lat is None or lon is None or data_type is None:
                        logger.error(f"Missing parameters for climate data tool - lat: {lat}, lon: {lon}, data_type: {data_type}")
                        result = {"error": "Lat, lon, and data_type parameters are required"}
                    else:
                        logger.debug(f"Getting {data_type} data for coordinates: {lat}, {lon}" + (f" for year {year}" if year else ""))
                        result = tool_get_climate_data_by_location(float(lat), float(lon), data_type, year)
                        # Format the result for better display
                        if isinstance(result, dict) and (result.get("success") or result.get("error")):
                            formatted_result = format_agricultural_data(result)
                            result = {"formatted_response": formatted_result, "raw_data": result}
                        
                elif name == "get_commodity_list":
                    logger.debug("Getting commodity list")
                    result = tool_get_commodity_list()
                    
                elif name == "get_geographies":
                    logger.debug("Getting geographies")
                    result = tool_get_geographies()
                    
                elif name == "get_markets_for_commodity":
                    commodity_id = args.get("commodity_id")
                    state_id = args.get("state_id")
                    district_id = args.get("district_id")
                    indicator = args.get("indicator", "price")
                    
                    if commodity_id is None or state_id is None or district_id is None:
                        logger.error(f"Missing parameters for markets tool - commodity_id: {commodity_id}, state_id: {state_id}, district_id: {district_id}")
                        result = {"error": "commodity_id, state_id, and district_id parameters are required"}
                    else:
                        logger.debug(f"Getting markets for commodity {commodity_id}, state {state_id}, district {district_id}")
                        result = tool_get_markets_for_commodity(int(commodity_id), int(state_id), int(district_id), indicator)
                        
                elif name == "get_commodity_prices":
                    commodity_id = args.get("commodity_id")
                    state_id = args.get("state_id")
                    district_ids = args.get("district_id")
                    market_ids = args.get("market_id")
                    from_date = args.get("from_date")
                    to_date = args.get("to_date")
                    
                    if commodity_id is None or state_id is None or from_date is None or to_date is None:
                        logger.error(f"Missing required parameters for commodity prices tool")
                        result = {"error": "commodity_id, state_id, from_date, and to_date parameters are required"}
                    else:
                        logger.debug(f"Getting prices for commodity {commodity_id}")
                        result = tool_get_commodity_prices(
                            int(commodity_id), 
                            int(state_id), 
                            district_ids, 
                            market_ids, 
                            from_date, 
                            to_date
                        )
                        # Format the result for better display
                        if isinstance(result, dict) and (result.get("success") or result.get("error")):
                            formatted_result = format_agricultural_data(result)
                            result = {"formatted_response": formatted_result, "raw_data": result}
                            
                elif name == "get_commodity_quantities":
                    commodity_id = args.get("commodity_id")
                    state_id = args.get("state_id")
                    district_ids = args.get("district_id")
                    market_ids = args.get("market_id")
                    from_date = args.get("from_date")
                    to_date = args.get("to_date")
                    
                    if commodity_id is None or state_id is None or from_date is None or to_date is None:
                        logger.error(f"Missing required parameters for commodity quantities tool")
                        result = {"error": "commodity_id, state_id, from_date, and to_date parameters are required"}
                    else:
                        logger.debug(f"Getting quantities for commodity {commodity_id}")
                        result = tool_get_commodity_quantities(
                            int(commodity_id), 
                            int(state_id), 
                            district_ids, 
                            market_ids, 
                            from_date, 
                            to_date
                        )
                        # Format the result for better display
                        if isinstance(result, dict) and (result.get("success") or result.get("error")):
                            formatted_result = format_agricultural_data(result)
                            result = {"formatted_response": formatted_result, "raw_data": result}
                            
                elif name == "get_commodity_prices_by_location":
                    lat = args.get("lat")
                    lon = args.get("lon")
                    commodity_name = args.get("commodity_name")
                    from_date = args.get("from_date")
                    to_date = args.get("to_date")
                    
                    if lat is None or lon is None or commodity_name is None or from_date is None or to_date is None:
                        logger.error(f"Missing parameters for commodity prices by location tool")
                        result = {"error": "lat, lon, commodity_name, from_date, and to_date parameters are required"}
                    else:
                        logger.debug(f"Getting prices for {commodity_name} near coordinates: {lat}, {lon}")
                        result = tool_get_commodity_prices_by_location(
                            float(lat), 
                            float(lon), 
                            commodity_name,
                            from_date, 
                            to_date
                        )
                        # Format the result for better display
                        if isinstance(result, dict) and (result.get("success") or result.get("error")):
                            formatted_result = format_agricultural_data(result)
                            result = {"formatted_response": formatted_result, "raw_data": result}
                            
                elif name == "get_commodity_price_by_name_and_location":
                    commodity_name = args.get("commodity_name")
                    state_name = args.get("state_name")
                    district_name = args.get("district_name")
                    from_date = args.get("from_date", "2025-07-18")  # Default to 30 days ago
                    to_date = args.get("to_date", "2025-08-18")      # Default to today
                    
                    if commodity_name is None or state_name is None or district_name is None:
                        logger.error(f"Missing parameters for commodity price by name and location tool")
                        result = {"error": "commodity_name, state_name, and district_name parameters are required"}
                    else:
                        logger.debug(f"Getting prices for {commodity_name} in {district_name}, {state_name}")
                        result = tool_get_commodity_price_by_name_and_location(
                            commodity_name,
                            state_name,
                            district_name,
                            from_date,
                            to_date
                        )
                        # Format the result for better display
                        if isinstance(result, dict) and (result.get("success") or result.get("error")):
                            formatted_result = format_agricultural_data(result)
                            result = {"formatted_response": formatted_result, "raw_data": result}

                elif name == "get_commodity_price_by_location_and_name":
                    commodity_name = args.get("commodity_name")
                    lat = args.get("lat")
                    lon = args.get("lon")
                    from_date = args.get("from_date", "2025-07-18")  # Default to 30 days ago
                    to_date = args.get("to_date", "2025-08-18")      # Default to today
                    
                    if commodity_name is None or lat is None or lon is None:
                        logger.error(f"Missing parameters for commodity price by location and name tool")
                        result = {"error": "commodity_name, lat, and lon parameters are required"}
                    else:
                        logger.debug(f"Getting prices for {commodity_name} near coordinates {lat}, {lon}")
                        result = tool_get_commodity_price_by_location_and_name(
                            commodity_name,
                            float(lat),
                            float(lon),
                            from_date,
                            to_date
                        )
                        # Format the result for better display
                        if isinstance(result, dict) and (result.get("success") or result.get("error")):
                            formatted_result = format_agricultural_data(result)
                            result = {"formatted_response": formatted_result, "raw_data": result}

                elif name == "intelligent_commodity_price_query":
                    query = args.get("query")
                    lat = args.get("lat")
                    lon = args.get("lon")
                    user_location = args.get("user_location")
                    
                    if query is None:
                        logger.error(f"Missing query parameter for intelligent commodity price query tool")
                        result = {"error": "query parameter is required"}
                    else:
                        logger.debug(f"Processing intelligent commodity query: {query}")
                        result = tool_intelligent_commodity_price_query(
                            query,
                            lat,
                            lon,
                            user_location
                        )
                        # Format the result for better display
                        if isinstance(result, dict) and (result.get("success") or result.get("error")):
                            formatted_result = format_agricultural_data(result)
                            result = {"formatted_response": formatted_result, "raw_data": result}
                        
                else:
                    logger.error(f"Unknown tool function: {name}")
                    result = {"error": f"Unknown tool function: {name}"}
                
                # Log tool execution result
                if result.get("error"):
                    logger.warning(f"Tool {name} returned error: {result['error']}")
                else:
                    logger.info(f"Tool {name} executed successfully")
                    
            except Exception as e:
                logger.error(f"Tool execution error for {name}: {str(e)}", exc_info=True)
                result = {"error": f"Tool execution error: {str(e)}"}
        
        tool_msg = {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": name,
            "content": json.dumps(result, indent=2)
        }
        tool_msgs.append(tool_msg)
        logger.debug(f"Tool message created for {name}")
    
    logger.debug(f"Completed tool call handling, returning {len(tool_msgs)} messages")
    return tool_msgs
