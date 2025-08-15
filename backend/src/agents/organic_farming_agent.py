"""
Organic Farming Guide Agent - Specialized in organic farming advice and guidance.
"""

import logging
import re
from typing import List
from .base_agent import BaseAgent
from .tools.registry import tool_registry

logger = logging.getLogger(__name__)

class OrganicFarmingAgent(BaseAgent):
    """Agent specialized in organic farming guidance and advice."""
    
    def __init__(self, llm):
        system_prompt = """You are an expert Organic Farming Guide with extensive knowledge in sustainable agriculture practices. 

Your expertise includes:
- Organic crop cultivation techniques
- Natural pest and disease management
- Soil health and composting
- Organic fertilizers and amendments
- Crop rotation and companion planting
- Sustainable farming practices
- Organic certification processes
- Natural weed control methods
- Beneficial insects and biodiversity
- Water conservation in organic farming
- Seasonal farming calendars
- Organic seed selection and saving

IMPORTANT: You have access to tools that can help provide current information:
- get_weather: Get weather information for farming decisions
- calculate: Perform calculations for farming economics and measurements

TOOL USAGE INSTRUCTIONS:
When users ask about weather conditions for farming, use:
TOOL_CALL: get_weather("location")

When users need calculations for farming (area, quantities, costs, etc.), use:
TOOL_CALL: calculate("mathematical_expression")

Examples:
User: "What's the weather like for planting tomatoes?"
You: "Let me check the current weather conditions for your farming area. TOOL_CALL: get_weather("your_location")"

User: "How much compost do I need for a 100 square meter garden?"
You: "I'll calculate the compost requirements for your garden. TOOL_CALL: calculate("100 * 0.05")"

Always consider:
- Environmental sustainability
- Soil health preservation
- Natural ecosystem balance
- Chemical-free solutions
- Long-term farm productivity

Be specific with recommendations and explain the reasoning behind organic practices. If asked about non-organic methods, gently redirect to organic alternatives."""
        
        super().__init__("Organic Farming Guide", llm, system_prompt)
        self.tools = tool_registry.get_all_tools()
        self.tool_map = {tool.name: tool for tool in self.tools}
    
    def can_handle(self, query: str) -> bool:
        """Check if this agent can handle the farming-related query."""
        farming_keywords = self.get_keywords()
        query_lower = query.lower()
        
        # Check for farming-related keywords
        return any(keyword in query_lower for keyword in farming_keywords)
    
    def get_keywords(self) -> List[str]:
        """Return keywords related to organic farming."""
        return [
            "organic", "farming", "agriculture", "crop", "soil", "compost", 
            "fertilizer", "pest", "disease", "weed", "plant", "grow", "harvest",
            "seed", "irrigation", "cultivation", "sustainable", "natural",
            "pesticide", "herbicide", "rotation", "companion planting",
            "biodiversity", "ecosystem", "farm", "garden", "vegetables",
            "fruits", "grains", "livestock", "poultry", "dairy", "organic certification"
        ]

    async def process(self, message: str, conversation_history=None) -> str:
        """Process farming queries with tool support."""
        try:
            # Process the message
            response = await super().process(message, conversation_history)
            
            # Check if response contains tool calls
            if "TOOL_CALL:" in response:
                return await self._handle_tool_calls(response, message, conversation_history)
            
            return response
        except Exception as e:
            logger.error(f"Error in organic farming agent process: {e}")
            return f"I apologize, but I encountered an error while processing your farming question: {str(e)}"
    
    async def _handle_tool_calls(self, response: str, original_message: str, conversation_history=None) -> str:
        """Handle tool calls in the response."""
        logger.info(f"Processing tool calls in farming response: {response[:200]}...")
        
        # Enhanced regex pattern to capture tool calls
        pattern = r'TOOL_CALL:\s*(\w+)\((.*?)\)'
        matches = re.findall(pattern, response)
        
        if not matches:
            logger.warning("No tool calls found despite TOOL_CALL being in response")
            return response
        
        tool_results = []
        for match in matches:
            tool_name, params = match
            logger.info(f"Attempting to call tool: {tool_name} with params: {params}")
            
            if tool_name in self.tool_map:
                try:
                    # Clean up parameters
                    param_value = params.strip().strip('"').strip("'").strip() if params.strip() else ""
                    
                    # Call the tool
                    result = self.tool_map[tool_name].invoke(param_value)
                    logger.info(f"Tool {tool_name} executed successfully")
                    
                    # Format the result nicely
                    if tool_name == 'get_weather':
                        if isinstance(result, dict) and 'error' not in result:
                            location = result.get('location', 'Unknown')
                            temp = result.get('temperature', {})
                            current_temp = temp.get('current', 'N/A')
                            conditions = result.get('conditions', 'N/A')
                            tool_results.append(f"🌤️ Weather for {location}: {current_temp}°C, {conditions}")
                        else:
                            tool_results.append(f"❌ Weather data unavailable")
                    elif tool_name == 'calculate':
                        tool_results.append(f"🧮 Calculation: {param_value} = **{result}**")
                    else:
                        tool_results.append(f"✅ {tool_name}: {result}")
                        
                except Exception as e:
                    logger.error(f"Error calling tool {tool_name}: {e}")
                    tool_results.append(f"❌ {tool_name} error: {str(e)}")
            else:
                logger.warning(f"Tool {tool_name} not found")
                tool_results.append(f"❌ Tool {tool_name} not available")
        
        if tool_results:
            # Create a comprehensive response
            combined_response = "Here's the information to help with your organic farming:\n\n"
            for result in tool_results:
                combined_response += f"{result}\n"
            
            # Add organic farming context
            combined_response += "\n🌱 **Organic Farming Recommendations:**\n"
            combined_response += "Based on this information, here are sustainable farming suggestions:\n"
            combined_response += "- Use organic, chemical-free methods in all practices\n"
            combined_response += "- Focus on soil health through composting and natural amendments\n"
            combined_response += "- Implement companion planting for natural pest control\n"
            combined_response += "- Consider weather patterns for optimal planting and harvesting\n"
            
            return combined_response
        
        return response