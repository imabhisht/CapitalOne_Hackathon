"""
Initialization file for the tools package.
"""
# Import all tool functions to make them accessible from the package level
from .weather_tool import tool_get_weather_by_coords
from .location_tool import tool_get_lat_lon_from_browser
from .datetime_tool import tool_get_date_time
from .agriculture_tool import tool_get_crop_data_by_location, tool_get_irrigation_data_by_location, tool_get_climate_data_by_location
from .commodity_tool import (
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
from .soil_water_content_tool import (
    tool_get_soil_water_content,
    tool_create_swc_subscription,
    tool_get_swc_statistics,
    tool_get_swc_product_info,
    tool_analyze_soil_conditions
)

# For backward compatibility, we'll also import the helper function
from .location_tool import get_browser_location