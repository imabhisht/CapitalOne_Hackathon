"""
Tool registry for managing all available tools.
"""

from typing import List
from langchain_core.tools import BaseTool

from .location_tool import get_location
from .weather_tool import get_weather
from .calculator_tool import calculate

class ToolRegistry:
    """
    Registry for managing all available tools.
    """
    
    def __init__(self):
        self._tools = {
            "get_location": get_location,
            "get_weather": get_weather,
            "calculate": calculate,
        }
    
    def get_all_tools(self) -> List[BaseTool]:
        """
        Get all available tools as a list.
        
        Returns:
            List of all registered tools
        """
        return list(self._tools.values())
    
    def get_tool(self, name: str) -> BaseTool:
        """
        Get a specific tool by name.
        
        Args:
            name: Name of the tool to retrieve
            
        Returns:
            The requested tool
            
        Raises:
            KeyError: If tool is not found
        """
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found. Available tools: {list(self._tools.keys())}")
        return self._tools[name]
    
    def get_tool_names(self) -> List[str]:
        """
        Get names of all available tools.
        
        Returns:
            List of tool names
        """
        return list(self._tools.keys())
    
    def register_tool(self, name: str, tool: BaseTool):
        """
        Register a new tool.
        
        Args:
            name: Name to register the tool under
            tool: The tool to register
        """
        self._tools[name] = tool

# Global tool registry instance
tool_registry = ToolRegistry()