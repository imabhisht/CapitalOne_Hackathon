# Enhanced Commodity Price Tool - Complete Workflow

## Overview

The enhanced commodity price tool now provides a comprehensive solution for querying agricultural commodity prices in India using the CEDA API. It implements an intelligent workflow that handles the complete process from user query to price retrieval.

## Key Features

### 1. **Intelligent Query Processing**
- Natural language query parsing
- Automatic commodity name recognition
- Smart location detection from text or coordinates
- Fallback mechanisms for missing information

### 2. **Multi-Modal Location Handling**
- **Coordinates to Location**: Reverse geocoding using Google Maps API
- **Text to Location**: State/district name parsing and fuzzy matching
- **User Location**: Browser geolocation integration

### 3. **Robust Workflow Implementation**
The tool implements the complete CEDA API workflow:
1. **Commodity Identification**: Find commodity ID from name
2. **Location Resolution**: Convert location to state/district IDs
3. **Market Discovery**: Get available markets for the commodity
4. **Price Retrieval**: Fetch current market prices

### 4. **Enhanced Matching**
- Fuzzy matching for location names
- Handles variations like "Nagpur" vs "Nagpur Division"
- Multiple matching strategies for better accuracy

## Available Tools

### 1. `tool_intelligent_commodity_price_query`
**Best for natural language queries**
```python
# Handles queries like:
# "What is the price of cotton?"
# "cotton rates in Maharashtra"
# "price of rice in my area"

result = tool_intelligent_commodity_price_query(
    query="What is the price of cotton in Maharashtra?",
    lat=21.1458,  # Optional: user coordinates
    lon=79.0882,  # Optional: user coordinates
    user_location="Nagpur, Maharashtra"  # Optional: user location text
)
```

### 2. `tool_get_commodity_price_by_location_and_name`
**Best when you have coordinates and commodity name**
```python
result = tool_get_commodity_price_by_location_and_name(
    commodity_name="Cotton",
    lat=21.1458,
    lon=79.0882,
    from_date="2025-07-18",
    to_date="2025-08-18"
)
```

### 3. `tool_get_commodity_price_by_name_and_location`
**Best when you have specific location names**
```python
result = tool_get_commodity_price_by_name_and_location(
    commodity_name="Cotton",
    state_name="Maharashtra",
    district_name="Nagpur",
    from_date="2025-07-18",
    to_date="2025-08-18"
)
```

## Complete Workflow Example

### User Query: "What's the price of cotton?"

1. **Query Analysis**: Extract "cotton" as commodity
2. **Location Detection**: 
   - Try to get user's coordinates
   - If available, reverse geocode to state/district
   - If not available, ask user for location
3. **Commodity Resolution**: Find "Cotton" in CEDA commodity list
4. **Location Resolution**: Find state/district IDs in CEDA geography data
5. **Market Discovery**: Get markets selling cotton in that location
6. **Price Retrieval**: Fetch current prices from all relevant markets
7. **Response Formatting**: Present prices with market names and dates

### User Query: "cotton price in Nagpur Maharashtra"

1. **Query Analysis**: Extract "cotton" and "Nagpur, Maharashtra"
2. **Direct Processing**: Use location names directly
3. **Fuzzy Matching**: Handle variations in district names
4. **Continue with workflow steps 3-7 above**

## Integration with Chatbot

### System Prompt Enhancement
The system prompt has been enhanced to:
- Prioritize the intelligent commodity query tool for price questions
- Handle location-based queries effectively
- Provide clear guidance on tool selection
- Include commodity price workflow instructions

### Tool Selection Logic
```
For commodity price queries:
1. First priority: intelligent_commodity_price_query (natural language)
2. If specific location provided: get_commodity_price_by_name_and_location
3. If coordinates available: get_commodity_price_by_location_and_name
4. If location detection fails: Ask for state and district names
```

## Error Handling

### Common Issues and Solutions

1. **Location Not Found**
   - Fuzzy matching attempts multiple variations
   - Provides suggestions for correct spelling
   - Falls back to asking for manual input

2. **Commodity Not Found**
   - Shows list of available commodities
   - Suggests similar commodity names
   - Handles common aliases (e.g., "cotton" → "Cotton")

3. **No Markets Found**
   - Suggests trying different locations
   - Recommends checking nearby districts
   - Provides alternative commodity suggestions

4. **API Rate Limits**
   - Implements intelligent retry mechanisms
   - Uses caching for repeated queries
   - Provides meaningful error messages

## Testing

### Test Files
- `test_enhanced_commodity_workflow.py`: Complete workflow testing
- `test_simple_commodity.py`: Basic functionality testing
- `check_geographies.py`: CEDA database exploration

### Running Tests
```bash
# Basic functionality test
python test_simple_commodity.py

# Complete workflow test (requires all API keys)
python test_enhanced_commodity_workflow.py

# Check available geographies
python check_geographies.py
```

## Configuration Requirements

### Environment Variables
```bash
# Required
CEDA_API_KEY=your_ceda_api_key

# Optional (for reverse geocoding)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key

# Optional (for chatbot integration)
OPENROUTER_API_KEY=your_openrouter_api_key
```

### API Key Setup
1. **CEDA API**: Register at [CEDA Ashoka](https://api.ceda.ashoka.edu.in/)
2. **Google Maps**: Enable Geocoding API in Google Cloud Console
3. **OpenRouter**: Register at [OpenRouter](https://openrouter.ai/) for LLM access

## Usage Examples

### In Streamlit Chatbot
```
User: "What's the price of cotton in my area?"
Bot: [Uses intelligent_commodity_price_query with location detection]

User: "cotton rates in nagpur"
Bot: [Parses query and uses fuzzy matching for location]

User: "price of rice in West Bengal"
Bot: [Uses name_and_location tool with state-level query]
```

### Direct API Usage
```python
from app.modules.tools.commodity_tool import tool_intelligent_commodity_price_query

# Natural language query
result = tool_intelligent_commodity_price_query(
    query="cotton price in Maharashtra",
    lat=21.1458,
    lon=79.0882
)

if result.get("success"):
    prices = result.get("prices", [])
    for price in prices:
        print(f"Market: {price['market']}")
        print(f"Price: ₹{price['modal_price']} per quintal")
        print(f"Date: {price['date']}")
```

## Benefits of Enhanced Implementation

1. **User-Friendly**: Handles natural language queries
2. **Robust**: Multiple fallback mechanisms
3. **Accurate**: Fuzzy matching for location names
4. **Comprehensive**: Complete workflow implementation
5. **Efficient**: Caching and rate limit handling
6. **Scalable**: Modular design for easy extension

This enhanced commodity tool transforms the user experience from requiring specific knowledge of state/district IDs to simply asking natural language questions about commodity prices.
