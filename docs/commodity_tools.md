# Commodity Price Tools Documentation

The Krishi Mitra application includes tools for accessing agricultural commodity prices from the CEDA Agmarknet API. These tools provide farmers with up-to-date market price information to help them make informed selling decisions.

## Prerequisites

To use the commodity price tools, you need to:

1. Obtain a CEDA API key from [https://api.ceda.ashoka.edu.in/](https://api.ceda.ashoka.edu.in/)
2. Add the key to your `.env` file as `CEDA_API_KEY=your_key_here`

## Available Tools

### 1. Get Commodity List (`get_commodity_list`)

Retrieves a list of all agricultural commodities available in the CEDA Agmarknet database.

**Parameters**: None

**Response**:
```json
{
  "success": true,
  "commodities": [
    {
      "id": 1,
      "name": "Rice"
    },
    {
      "id": 2,
      "name": "Wheat"
    }
  ]
}
```

### 2. Get Geographies (`get_geographies`)

Retrieves a list of all states and districts available in the CEDA Agmarknet database.

**Parameters**: None

**Response**:
```json
{
  "success": true,
  "geographies": [
    {
      "state_id": 1,
      "state_name": "Andhra Pradesh",
      "districts": [
        {
          "district_id": 1,
          "district_name": "Anantapur"
        }
      ]
    }
  ]
}
```

### 3. Get Markets for Commodity (`get_markets_for_commodity`)

Retrieves a list of markets for a given commodity, state, and district.

**Parameters**:
- `commodity_id` (integer, required): Commodity ID from the commodity list
- `state_id` (integer, required): State ID from geographies
- `district_id` (integer, required): District ID from geographies
- `indicator` (string, required): Must be "price" or "quantity"

**Response**:
```json
{
  "success": true,
  "markets": [
    {
      "census_state_id": 1,
      "census_district_id": 1,
      "market_id": 1,
      "market_name": "Anantapur Market"
    }
  ]
}
```

### 4. Get Commodity Prices (`get_commodity_prices`)

Retrieves price data for a commodity at the state, district, or market level.

**Parameters**:
- `commodity_id` (integer, required): Commodity ID
- `state_id` (integer, required): State ID (use 0 for all India level data)
- `district_id` (array of integers, optional): District IDs
- `market_id` (array of integers, optional): Market IDs
- `from_date` (string, required): Start date (format: YYYY-MM-DD)
- `to_date` (string, required): End date (format: YYYY-MM-DD)

**Response**:
```json
{
  "success": true,
  "prices": [
    {
      "date": "2025-01-01",
      "commodity_id": 1,
      "census_state_id": 1,
      "census_district_id": 1,
      "market_id": 1,
      "min_price": 2000,
      "max_price": 2500,
      "modal_price": 2200
    }
  ],
  "count": 1
}
```

### 5. Get Commodity Quantities (`get_commodity_quantities`)

Retrieves quantity data for a commodity at the state, district, or market level.

**Parameters**:
- `commodity_id` (integer, required): Commodity ID
- `state_id` (integer, required): State ID (use 0 for all India level data)
- `district_id` (array of integers, optional): District IDs
- `market_id` (array of integers, optional): Market IDs
- `from_date` (string, required): Start date (format: YYYY-MM-DD)
- `to_date` (string, required): End date (format: YYYY-MM-DD)

**Response**:
```json
{
  "success": true,
  "quantities": [
    {
      "date": "2025-01-01",
      "commodity_id": 1,
      "census_state_id": 1,
      "census_district_id": 1,
      "market_id": 1,
      "quantity": 1000
    }
  ],
  "count": 1
}
```

### 6. Get Commodity Prices by Location (`get_commodity_prices_by_location`)

Retrieves commodity prices for the nearest district/state based on latitude and longitude. *Note: This tool requires district/state mapping which may not be fully implemented yet.*

**Parameters**:
- `lat` (number, required): Latitude in decimal degrees
- `lon` (number, required): Longitude in decimal degrees
- `commodity_name` (string, required): Name of the commodity
- `from_date` (string, required): Start date (format: YYYY-MM-DD)
- `to_date` (string, required): End date (format: YYYY-MM-DD)

**Response**:
```json
{
  "error": "Reverse geocoding for district/state not yet implemented. Please provide district and state directly.",
  "suggestion": "Use the get_geographies tool to find available states and districts, then use get_commodity_prices with specific state and district IDs."
}
```

### 7. Get Commodity Price by Name and Location (`get_commodity_price_by_name_and_location`)

Retrieves commodity prices by commodity name and location names (state and district). This tool handles the full workflow:
1. Finds commodity ID by name
2. Finds state and district IDs by names
3. Gets markets for the commodity in that location
4. Gets prices for those markets

**Parameters**:
- `commodity_name` (string, required): Name of the commodity (e.g., "Cotton", "Rice")
- `state_name` (string, required): Name of the state (e.g., "Maharashtra", "Andhra Pradesh")
- `district_name` (string, required): Name of the district (e.g., "Nagpur", "Anantapur")
- `from_date` (string, optional): Start date (format: YYYY-MM-DD, default: 30 days ago)
- `to_date` (string, optional): End date (format: YYYY-MM-DD, default: today)

**Response**:
```json
{
  "success": true,
  "commodity": "Cotton",
  "location": {
    "state": "Maharashtra",
    "district": "Nagpur"
  },
  "date_range": {
    "from": "2025-07-18",
    "to": "2025-08-18"
  },
  "prices": [
    {
      "date": "2025-08-15",
      "market": "Nagpur Market",
      "min_price": 4500,
      "max_price": 5200,
      "modal_price": 4800,
      "unit": "₹/Quintal"
    }
  ],
  "count": 1
}
```

## Usage Examples

1. "What are the current prices for rice in Andhra Pradesh?"
2. "How have wheat prices changed in my district over the past month?"
3. "What are the prices for cotton in my state?"
4. "What is the price of cotton in Nagpur district, Maharashtra?"

## Implementation Details

The commodity tools are implemented in `app/modules/tools/commodity_tool.py` and integrated with the OpenRouter API through `app/modules/api.py`. The tools follow the same pattern as other tools in the application:

1. Each tool function starts with `tool_get_` prefix
2. They return structured JSON responses with success/error indicators
3. They use proper logging for debugging and monitoring
4. They handle API errors gracefully
5. They're integrated with the Streamlit UI through the tool calling mechanism

## Future Improvements

1. Complete the reverse geocoding functionality for the `get_commodity_prices_by_location` tool
2. Add caching for API responses to reduce load and improve performance
3. Implement data visualization for price trends
4. Add alerts for significant price changes