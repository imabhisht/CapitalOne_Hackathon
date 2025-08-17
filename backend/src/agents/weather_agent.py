"""
Weather Agent - Specialized in weather information and agricultural weather advice.
"""

import logging
from typing import List
from .base_agent import BaseAgent
from .tools.registry import tool_registry

logger = logging.getLogger(__name__)

class WeatherAgent(BaseAgent):
    """Agent specialized in weather information and agricultural weather guidance."""
    
    def __init__(self, llm):
        system_prompt = """You are a Weather and Agricultural Meteorology Expert with deep knowledge of weather patterns and their impact on farming.

Your expertise includes:
- Current weather conditions and forecasts
- Agricultural weather planning
- Seasonal weather patterns
- Weather impact on crop growth and development
- Irrigation planning based on weather
- Pest and disease risk assessment related to weather
- Optimal planting and harvesting times
- Weather-related farming decisions
- Climate change impacts on agriculture
- Microclimate considerations

IMPORTANT: You have access to the following tools that you MUST use when appropriate:
- get_location: Get the user's current location coordinates
- get_weather: Get weather information for specific coordinates (requires lat/lon)

TOOL USAGE INSTRUCTIONS:
For weather queries, you MUST follow this sequence:
1. First get location: TOOL_CALL: get_location()
2. Then get weather: TOOL_CALL: get_weather(latitude, longitude)

When users ask about weather without specifying location, use:
TOOL_CALL: get_location()

When you have coordinates, get weather with:
TOOL_CALL: get_weather(lat, lon)

ALWAYS use these tools for current weather data. Do NOT provide weather information without using the tools first.

Example responses:
User: "What's the weather today?"
You: "I'll check the current weather conditions for your location. First, let me get your location. TOOL_CALL: get_location()"

User: "What's the weather like for farming?"
You: "Let me get your location and then check the current weather conditions. TOOL_CALL: get_location()"

Focus on practical implications for farming and agriculture when discussing weather."""
        
        super().__init__("Weather Expert", llm, system_prompt)
        self.tools = tool_registry.get_all_tools()
        self.tool_map = {tool.name: tool for tool in self.tools}
    
    def can_handle(self, query: str) -> bool:
        """Check if this agent can handle the weather query."""
        weather_keywords = self.get_keywords()
        query_lower = query.lower()
        
        return any(keyword in query_lower for keyword in weather_keywords)
    
    def get_keywords(self) -> List[str]:
        """Return keywords related to weather."""
        return [
            "weather", "temperature", "rain", "precipitation", "humidity",
            "wind", "forecast", "climate", "sunny", "cloudy", "storm",
            "drought", "flood", "frost", "heat", "cold", "season",
            "monsoon", "winter", "summer", "spring", "autumn", "fall",
            "irrigation", "watering", "planting time", "harvest time",
            "growing season", "weather conditions", "atmospheric"
        ]
    
    async def process(self, message: str, conversation_history=None) -> str:
        """Process weather queries with tool support."""
        try:
            # Always try to get weather information for weather-related queries
            response = await super().process(message, conversation_history)
            
            # Check if response contains tool calls
            if "TOOL_CALL:" in response:
                return await self._handle_tool_calls(response, message, conversation_history)
            
            return response
        except Exception as e:
            logger.error(f"Error in weather agent process: {e}")
            return f"I apologize, but I encountered an error while processing your weather request: {str(e)}"
    
    async def _handle_tool_calls(self, response: str, original_message: str, conversation_history=None) -> str:
        """Handle tool calls in the response."""
        import re
        
        logger.info(f"Processing tool calls in response: {response[:200]}...")
        
        # Enhanced regex pattern to capture tool calls
        pattern = r'TOOL_CALL:\s*(\w+)\((.*?)\)'
        matches = re.findall(pattern, response)
        
        if not matches:
            logger.warning("No tool calls found despite TOOL_CALL being in response")
            return response
        
        tool_results = []
        location_data = None
        
        for match in matches:
            tool_name, params = match
            logger.info(f"Attempting to call tool: {tool_name} with params: {params}")
            
            if tool_name in self.tool_map:
                try:
                    # Handle different tool types
                    if tool_name == 'get_location':
                        # No parameters needed for location
                        result = self.tool_map[tool_name].invoke()
                        logger.info(f"Tool {tool_name} executed successfully")
                        
                        if isinstance(result, dict) and 'error' not in result and result.get('success'):
                            location_data = result
                            lat = result.get('latitude')
                            lon = result.get('longitude')
                            tool_results.append(f"📍 Location found: {lat}, {lon}")
                        else:
                            tool_results.append(f"❌ Location error: {result.get('error', 'Unknown error')}")
                            
                    elif tool_name == 'get_weather':
                        # Parse lat/lon parameters for weather
                        if location_data and 'latitude' in location_data and 'longitude' in location_data:
                            # Use location from previous call
                            lat = location_data['latitude']
                            lon = location_data['longitude']
                        else:
                            # Try to parse parameters
                            param_value = params.strip().strip('"').strip("'").strip()
                            if ',' in param_value:
                                coords = param_value.split(',')
                                lat = float(coords[0].strip())
                                lon = float(coords[1].strip())
                            else:
                                tool_results.append(f"❌ Weather error: Need coordinates. Call get_location() first.")
                                continue
                        
                        # Call weather tool with coordinates
                        result = self.tool_map[tool_name].invoke({'lat': lat, 'lon': lon})
                        logger.info(f"Tool {tool_name} executed successfully")
                        
                        # Format the result nicely
                        if isinstance(result, dict):
                            if 'error' in result:
                                tool_results.append(f"❌ {tool_name} error: {result['error']}")
                            else:
                                # Format weather data nicely
                                location_info = result.get('location', {})
                                current = result.get('current_weather', {})
                                temp_c = current.get('temperature', {}).get('celsius', 'N/A')
                                condition = current.get('condition', {}).get('text', 'N/A')
                                humidity = current.get('atmospheric', {}).get('humidity', 'N/A')
                                wind_kph = current.get('wind', {}).get('speed_kph', 'N/A')
                                
                                location_name = location_info.get('name', 'Unknown Location')
                                formatted_result = f"Weather for {location_name}: {temp_c}°C, {condition}, Humidity: {humidity}%, Wind: {wind_kph} km/h"
                                tool_results.append(f"🌤️ {formatted_result}")
                        else:
                            tool_results.append(f"📍 {tool_name} result: {result}")
                    else:
                        # Handle other tools normally
                        param_value = params.strip().strip('"').strip("'").strip() if params.strip() else ""
                        result = self.tool_map[tool_name].invoke(param_value)
                        tool_results.append(f"✅ {tool_name} result: {result}")
                        
                except Exception as e:
                    logger.error(f"Error calling tool {tool_name}: {e}")
                    tool_results.append(f"❌ {tool_name} error: {str(e)}")
            else:
                logger.warning(f"Tool {tool_name} not found in tool_map. Available tools: {list(self.tool_map.keys())}")
                tool_results.append(f"❌ Tool {tool_name} not available")
        
        if tool_results:
            # Create a comprehensive response with tool results
            combined_response = "Here's the current weather information:\n\n"
            for result in tool_results:
                combined_response += f"{result}\n"
            
            # Add agricultural context
            combined_response += "\n🌾 **Agricultural Implications:**\n"
            combined_response += "Based on these weather conditions, here are some farming considerations:\n"
            combined_response += "- Monitor soil moisture levels for optimal irrigation timing\n"
            combined_response += "- Adjust planting schedules based on temperature trends\n"
            combined_response += "- Consider weather impact on pest and disease pressure\n"
            combined_response += "- Plan harvesting activities around favorable conditions\n"
            
            return combined_response
        
        return response