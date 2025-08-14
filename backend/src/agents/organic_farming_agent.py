"""
Organic Farming Guide Agent - Specialized in organic farming advice and guidance.
"""

import re
from typing import List
from .base_agent import BaseAgent

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

Provide practical, actionable advice based on organic farming principles. Always consider:
- Environmental sustainability
- Soil health preservation
- Natural ecosystem balance
- Chemical-free solutions
- Long-term farm productivity

Be specific with recommendations and explain the reasoning behind organic practices. If asked about non-organic methods, gently redirect to organic alternatives."""
        
        super().__init__("Organic Farming Guide", llm, system_prompt)
    
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