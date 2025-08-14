"""
Weather Agent - Specialized in weather information and agricultural weather advice.
"""

from typing import List
from .base_agent import BaseAgent
from .tools.registry import tool_registry

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

Available tools:
- get_weather: Get weather information for a location (use format: TOOL_CALL: get_weather("location"))
- get_location: Get location information (use format: TOOL_CALL: get_location())

When users ask about weather, always use the weather tool to get current information. Provide agricultural context and advice based on weather conditions.

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
        # Always try to get weather information for weather-related queries
        response = await super().process(message, conversation_history)
        
        # Check if response contains tool calls
        if "TOOL_CALL:" in response:
            return await self._handle_tool_calls(response, message, conversation_history)
        
        return response
    
    async def _handle_tool_calls(self, response: str, original_message: str, conversation_history=None) -> str:
        """Handle tool calls in the response."""
        import re
        
        # Extract tool calls
        pattern = r'TOOL_CALL:\s*(\w+)\((.*?)\)'
        matches = re.findall(pattern, response)
        
        tool_results = []
        for match in matches:
            tool_name, params = match
            if tool_name in self.tool_map:
                try:
                    # Remove quotes from params
                    param_value = params.strip().strip('"').strip("'") if params.strip() else ""
                    result = self.tool_map[tool_name].invoke(param_value)
                    tool_results.append(f"{tool_name} result: {result}")
                except Exception as e:
                    tool_results.append(f"{tool_name} error: {str(e)}")
        
        if tool_results:
            # Get a natural response based on tool results
            follow_up_message = f"Based on the weather data: {'; '.join(tool_results)}, please provide comprehensive weather analysis and agricultural advice for: {original_message}"
            return await super().process(follow_up_message, conversation_history)
        
        return response