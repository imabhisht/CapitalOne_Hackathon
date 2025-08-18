"""
System prompt generation logic.
"""
from typing import Optional, Dict
from .api import openrouter_tools_schema
from ..config import get_logger

# Initialize logger
logger = get_logger(__name__)

def generate_system_prompt(user_location: Optional[Dict] = None, manual_location: Optional[str] = None) -> str:
    logger.debug("Generating system prompt")
    logger.debug(f"User location data available: {user_location is not None}")
    logger.debug(f"Manual location provided: {manual_location is not None}")
    
    tool_schemas = openrouter_tools_schema()
    tool_descriptions = []
    
    for tool in tool_schemas:
        fn = tool.get("function", {})
        name = fn.get("name", "")
        desc = fn.get("description", "")
        params = fn.get("parameters", {}).get("properties", {})
        param_str = ""
        if params:
            param_list = [f"{k}: {v.get('description', '')}" for k, v in params.items()]
            param_str = " (" + ", ".join(param_list) + ")"
        tool_descriptions.append(f"- {name}{param_str}: {desc}")
    
    tools_section = "\n".join(tool_descriptions)
    logger.debug(f"Generated tool descriptions for {len(tool_schemas)} tools")
    
    base_prompt = f"""You are an intelligent, agriculture expert assistant with access to advanced location, weather, and context-aware tools. You MUST use these tools proactively to provide helpful, actionable, and data-driven advice for farmers, growers, and anyone seeking agricultural guidance.\n\nCRITICAL TOOL USAGE RULES:\n1. For ANY agriculture, weather, crop, soil, irrigation, or climate-related question (e.g., \"Should I irrigate today?\", \"Is it a good time to plant wheat?\", \"What is the weather for my farm?\"), you MUST attempt to get real data using your tools.\n\n2. When users ask location-based agricultural questions without specifying a location, ALWAYS start by calling the tool that gets the user's current coordinates (e.g., get_lat_lon_from_browser) to try to get their position.\n\n3. For advice questions (e.g., \"Should I water my crops?\", \"Is there a risk of frost?\", \"What is the best time to spray pesticides?\"), you MUST:\n   - First call the location tool to get coordinates\n   - Then call the relevant weather or context tool with those coordinates\n   - Provide specific, actionable agricultural advice based on the actual data\n\n4. If location tools fail, ask the user for their location but explain you tried to get it automatically.\n\n5. NEVER give generic responses to agricultural or weather questions - always try to get real data first.\n\nAvailable Tools (dynamically generated):\n{tools_section}\n\nTool Response Priority:\n- Use tools first, explain second\n- Provide specific, actionable advice based on real data\n- Only fall back to asking for location if tools fail"""
    
    location_context = []
    if user_location and not user_location.get("error"):
        lat, lon = user_location.get('lat'), user_location.get('lon')
        accuracy = user_location.get('accuracy', 'unknown')
        location_context.append(f"User's current browser location is available: {lat:.4f}, {lon:.4f} (accuracy: {accuracy}m)")
        logger.debug(f"Added browser location context: {lat:.4f}, {lon:.4f}")
    
    if manual_location:
        location_context.append(f"User provided location hint: {manual_location}")
        logger.debug(f"Added manual location context: {manual_location}")
    
    if location_context:
        base_prompt += f"\n\nLocation Context: " + " | ".join(location_context)
        logger.debug("Added location context to system prompt")
    
    logger.info(f"System prompt generated - Length: {len(base_prompt)} characters")
    return base_prompt
