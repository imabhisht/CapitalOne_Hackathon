"""
API call logic for OpenRouter and tool call handling.
"""
import os
import json
from openai import OpenAI
from typing import List, Dict, Optional
from dotenv import load_dotenv
from .tools import tool_get_weather_by_coords, tool_get_lat_lon_from_browser, tool_get_date_time
from ..config import get_logger

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
