"""
Tool registry for managing all available tools.
"""

from typing import List, Any, Callable


from .location_tool import get_location
from .weather_tool import get_weather
from .calculator_tool import calculate
from .crop_data_tool import get_crop_data


class ToolAdapter:
    """Adapter that normalizes a callable tool into an object with
    attributes agents expect: .name, .description and .invoke(...).
    """

    def __init__(self, func: Callable):
        self._func = func
        # Some tool decorators may already attach metadata; fall back to function attributes
        self.name = getattr(func, "name", getattr(func, "__name__", "unknown_tool"))
        # description may be present or use the docstring
        self.description = getattr(func, "description", func.__doc__ or "")

    def invoke(self, param: Any = None):
        """Call the underlying tool in a forgiving way.

        - If a dict is passed, call the tool with kwargs.
        - If a single value is passed, call the tool with that value as the first positional arg.
        - If None or empty string, call the tool with no arguments.
        """
        # Check if this is a LangChain tool (has run method)
        if hasattr(self._func, "run") and callable(getattr(self._func, "run")):
            # LangChain tools expect tool_input as the parameter
            if isinstance(param, dict):
                # For LangChain tools, we need to pass the dict as tool_input
                return self._func.run(tool_input=param)
            elif param is None or (isinstance(param, str) and param == ""):
                return self._func.run(tool_input={})
            else:
                return self._func.run(tool_input=param)
        
        # Check if this is a LangChain tool with invoke method
        elif hasattr(self._func, "invoke") and callable(getattr(self._func, "invoke")):
            # LangChain tools with invoke expect a dict input
            if isinstance(param, dict):
                return self._func.invoke(param)
            elif param is None or (isinstance(param, str) and param == ""):
                return self._func.invoke({})
            else:
                return self._func.invoke({"tool_input": param})
        
        # Fallback for regular callable functions
        elif callable(self._func):
            if isinstance(param, dict):
                return self._func(**param)
            elif param is None or (isinstance(param, str) and param == ""):
                return self._func()
            else:
                return self._func(param)
        
        else:
            raise TypeError("Tool object is not callable and has no run/invoke method")


class ToolRegistry:
    """Registry for managing all available tools.

    This registry wraps raw tool callables with ToolAdapter so the rest of
    the codebase can rely on .name, .description and .invoke(...).
    """

    def __init__(self):
        # Map of canonical name -> ToolAdapter
        self._tools = {
            "get_location": ToolAdapter(get_location),
            "get_weather": ToolAdapter(get_weather),
            "calculate": ToolAdapter(calculate),
            "get_crop_data": ToolAdapter(get_crop_data),
        }

    def get_all_tools(self) -> List[Any]:
        """Return a list of tool adapter objects."""
        return list(self._tools.values())

    def get_tool(self, name: str) -> Any:
        """Get a specific tool adapter by name.

        Raises KeyError if the tool is not registered.
        """
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found. Available tools: {list(self._tools.keys())}")
        return self._tools[name]

    def get_tool_names(self) -> List[str]:
        return list(self._tools.keys())

    def register_tool(self, name: str, func: Callable):
        """Register a new tool function under the given name."""
        self._tools[name] = ToolAdapter(func)


# Global tool registry instance
tool_registry = ToolRegistry()