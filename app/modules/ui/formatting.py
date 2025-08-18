"""
UI helper functions for formatting agricultural data.
"""
import json
from typing import Dict, Any

def format_agricultural_data(data: Dict[str, Any]) -> str:
    """
    Format agricultural data for better display in the UI.
    
    Args:
        data (Dict): Raw agricultural data from tools
        
    Returns:
        str: Formatted markdown string
    """
    if not data:
        return "No data available."
    
    # Handle error responses
    if data.get("error"):
        return f"⚠️ Error: {data.get('error')}"
    
    # Handle unsuccessful responses
    if not data.get("success", True):
        return f"ℹ️ {data.get('message', 'No data found.')}"
    
    # Format location information
    location_info = ""
    location = data.get("location")
    if location:
        location_info = f"📍 **Location**: {location.get('district', 'Unknown')}, {location.get('state', 'Unknown')}\\n"
        if location.get("latitude") and location.get("longitude"):
            location_info += f"   (Approx. {location['latitude']:.4f}°N, {location['longitude']:.4f}°E)\\n\\n"
    
    # Format the actual data
    formatted_data = ""
    data_content = data.get("data")
    
    if isinstance(data_content, list):
        # Multiple years of data
        if len(data_content) > 0:
            # Format as a table for multiple years
            formatted_data += "📊 **Historical Data**\\n\\n"
            
            # Get the data type to determine what columns to show
            data_type = data.get("data_type", "crop")
            
            if data_type == "crop":
                formatted_data += "| Year | Rice (k ha) | Wheat (k ha) | Total (k ha) |\\n"
                formatted_data += "|------|-------------|--------------|--------------|\\n"
                for item in data_content[:10]:  # Show only first 10 years
                    formatted_data += f"| {item.get('year', 'N/A')} | {item.get('rice_area', 'N/A'):.1f} | {item.get('wheat_area', 'N/A'):.1f} | {item.get('total_area', 'N/A'):.1f} |\\n"
                if len(data_content) > 10:
                    formatted_data += f"\\n*Showing 10 of {len(data_content)} years of data*\\n"
                    
            elif data_type == "temperature":
                formatted_data += "| Year | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |\\n"
                formatted_data += "|------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|\\n"
                for item in data_content[:5]:  # Show only first 5 years
                    months = []
                    for month in ["january", "february", "march", "april", "may", "june",
                                "july", "august", "september", "october", "november", "december"]:
                        temp = item.get(month)
                        months.append(f"{temp:.1f}" if temp is not None else "N/A")
                    formatted_data += f"| {item.get('year', 'N/A')} | {' | '.join(months)} |\\n"
                if len(data_content) > 5:
                    formatted_data += f"\\n*Showing 5 of {len(data_content)} years of data*\\n"
                    
            elif data_type == "precipitation":
                formatted_data += "| Year | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |\\n"
                formatted_data += "|------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|\\n"
                for item in data_content[:5]:  # Show only first 5 years
                    months = []
                    for month in ["january", "february", "march", "april", "may", "june",
                                "july", "august", "september", "october", "november", "december"]:
                        precip = item.get(month)
                        months.append(f"{precip:.1f}" if precip is not None else "N/A")
                    formatted_data += f"| {item.get('year', 'N/A')} | {' | '.join(months)} |\\n"
                if len(data_content) > 5:
                    formatted_data += f"\\n*Showing 5 of {len(data_content)} years of data*\\n"
                    
            else:  # Irrigation data
                formatted_data += "| Year | Canals (k ha) | Wells (k ha) | Tanks (k ha) | Total (k ha) |\\n"
                formatted_data += "|------|---------------|--------------|--------------|--------------|\\n"
                for item in data_content[:10]:  # Show only first 10 years
                    formatted_data += f"| {item.get('year', 'N/A')} | {item.get('canals_area', 'N/A'):.1f} | {item.get('total_well_area', 'N/A'):.1f} | {item.get('tanks_area', 'N/A'):.1f} | {item.get('canals_area', 0) + item.get('total_well_area', 0) + item.get('tanks_area', 0):.1f} |\\n"
                if len(data_content) > 10:
                    formatted_data += f"\\n*Showing 10 of {len(data_content)} years of data*\\n"
    else:
        # Single data point
        formatted_data += "📊 **Data Summary**\\n\\n"
        data_type = data.get("data_type", "crop")
        
        if data_type == "crop":
            formatted_data += f"- **Year**: {data_content.get('year', 'N/A')}\\n"
            formatted_data += f"- **Rice Area**: {data_content.get('rice_area', 'N/A'):.1f} thousand hectares\\n"
            formatted_data += f"- **Wheat Area**: {data_content.get('wheat_area', 'N/A'):.1f} thousand hectares\\n"
            formatted_data += f"- **Total Area**: {data_content.get('total_area', 'N/A'):.1f} thousand hectares\\n"
        elif data_type == "temperature":
            formatted_data += f"- **Year**: {data_content.get('year', 'N/A')}\\n"
            formatted_data += "- **Monthly Temperatures (°C)**:\\n"
            for month in ["january", "february", "march", "april", "may", "june",
                         "july", "august", "september", "october", "november", "december"]:
                temp = data_content.get(month)
                if temp is not None:
                    formatted_data += f"  - {month.capitalize()}: {temp:.1f}°C\\n"
        elif data_type == "precipitation":
            formatted_data += f"- **Year**: {data_content.get('year', 'N/A')}\\n"
            formatted_data += "- **Monthly Precipitation (mm)**:\\n"
            for month in ["january", "february", "march", "april", "may", "june",
                         "july", "august", "september", "october", "november", "december"]:
                precip = data_content.get(month)
                if precip is not None:
                    formatted_data += f"  - {month.capitalize()}: {precip:.1f} mm\\n"
        else:  # Irrigation data
            formatted_data += f"- **Year**: {data_content.get('year', 'N/A')}\\n"
            formatted_data += f"- **Canals Area**: {data_content.get('canals_area', 'N/A'):.1f} thousand hectares\\n"
            formatted_data += f"- **Tube Wells Area**: {data_content.get('tube_wells_area', 'N/A'):.1f} thousand hectares\\n"
            formatted_data += f"- **Tanks Area**: {data_content.get('tanks_area', 'N/A'):.1f} thousand hectares\\n"
            formatted_data += f"- **Total Irrigated Area**: {data_content.get('canals_area', 0) + data_content.get('tube_wells_area', 0) + data_content.get('tanks_area', 0):.1f} thousand hectares\\n"
    
    return location_info + formatted_data