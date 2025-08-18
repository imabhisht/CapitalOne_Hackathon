"""
Initialization file for the tools package.
"""
# Import all tool functions to make them accessible from the package level
from .weather_tool import tool_get_weather_by_coords
from .location_tool import tool_get_lat_lon_from_browser
from .datetime_tool import tool_get_date_time
from .agriculture_tool import tool_get_crop_data_by_location, tool_get_irrigation_data_by_location, tool_get_climate_data_by_location

# For backward compatibility, we'll also import the helper function
from .location_tool import get_browser_location