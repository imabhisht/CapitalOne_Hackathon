# Krishi Mitra - Agricultural Assistant for Indian Farmers

An intelligent agricultural assistant that helps Indian farmers make informed decisions about crops, weather, irrigation, market prices, and soil conditions.

## 🌾 Features

- **Location-aware assistance**: Uses browser geolocation to provide relevant information for your area
- **Enhanced weather forecasts**: 
  - Current weather conditions with detailed atmospheric data
  - Up to 14-day weather forecasts
  - Hourly weather predictions
  - Weather alerts and warnings
  - Historical weather data
  - Air quality information
- **Crop data**: Historical crop production data for your district
- **Irrigation information**: Data on irrigation sources in your area
- **Climate data**: Temperature and precipitation patterns
- **Market prices**: Commodity prices from the CEDA Agmarknet API
- **Soil water content monitoring**: Satellite-based soil moisture data for irrigation decisions
- **AI-powered insights**: Natural language interface for asking farming questions

## 🛠️ Prerequisites

- Python 3.8+
- MongoDB instance (local or remote)
- API keys for:
  - [OpenRouter](https://openrouter.ai/) (for AI model access)
  - [WeatherAPI](https://www.weatherapi.com/) (for weather data)
  - [Google Maps API](https://developers.google.com/maps/documentation/geocoding/get-api-key) (optional, for improved geocoding)
  - [CEDA API](https://api.ceda.ashoka.edu.in/) (for commodity prices)
  - [Planet API](https://www.planet.com/) (for soil water content data)

## 🚀 Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd hackathon-capital-one
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Copy the `.env.example` file to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` to add your keys:
   - `OPENROUTER_API_KEY` - Get from [OpenRouter](https://openrouter.ai/keys)
   - `WEATHERAPI_KEY` - Get from [WeatherAPI](https://www.weatherapi.com/)
   - `MONGODB_URI` - Your MongoDB connection string
   - `GOOGLE_MAPS_API_KEY` - Optional, for improved geocoding
   - `CEDA_API_KEY` - Get from [CEDA API](https://api.ceda.ashoka.edu.in/)
   - `PLANET_API_KEY` - Get from [Planet API](https://www.planet.com/)

5. **Load agricultural data:**
   Follow the instructions in `data/README.md` to load the agricultural datasets into MongoDB:
   ```bash
   cd data
   python data_loader.py
   python add_geolocation.py
   cd ..
   ```

6. **Run the application:**
   ```bash
   streamlit run streamlit_app.py
   ```

## 💬 Usage

Once the application is running, you can:

1. Ask questions in natural language like:
   - "What crops grow well in my area?"
   - "Should I irrigate my crops today?"
   - "What's the 7-day weather forecast for my farm?"
   - "Are there any weather warnings in my area?"
   - "What was the weather like last week for comparison?"
   - "What's the air quality today?"
   - "What are the current market prices for wheat in my district?"
   - "What is the soil water content in my area?"

2. The assistant will use your browser's location (if permitted) to provide location-specific information.

## 🧰 Available Tools

The assistant has access to several specialized tools:

### Weather Tool
- Current weather conditions with air quality data
- Weather forecasts up to 14 days ahead
- Hourly weather predictions
- Weather alerts and warnings
- Historical weather data from 2010 onwards

### Agricultural Data Tools
- Access crop production data for your district
- Irrigation source information
- Climate patterns and trends

### Commodity Price Tools
- Access real-time market prices for agricultural commodities (via CEDA API)
- Location-aware price comparisons
- Historical price analysis

### Soil Water Content Tool
- Satellite-based soil moisture monitoring
- Multiple spatial resolutions (20m, 100m, 1000m)
- Data from SMAP and AMSR2 satellite sensors
- Near-daily global updates
- Agricultural decision support for irrigation

### Location Tool
- Get your current coordinates
- Reverse geocoding to determine state/district

### Date/Time Tool
- Get the current date and time

## 💰 Market Price Queries

The application can fetch real-time commodity prices from the CEDA Agmarknet API. You can ask questions like:

- "What is the current price of wheat in Nagpur district?"
- "How have rice prices changed in my area over the past month?"
- "What are the market prices for cotton in Maharashtra?"

The system automatically:
1. Identifies the commodity from your query
2. Maps your location to the appropriate state and district
3. Finds relevant markets in your area
4. Retrieves current price information
5. Presents the data in an easy-to-understand format

## 🌱 Soil Water Content Monitoring

The application now includes satellite-based soil water content monitoring using Planet's API. You can ask questions like:

- "What is the soil moisture level in my field?"
- "Is my crop area getting enough water?"
- "Should I irrigate based on current soil conditions?"

Benefits:
- Near-daily global soil moisture measurements
- Multiple spatial resolutions for precise monitoring
- Data from multiple satellite sensors (SMAP, AMSR2)
- Agricultural decision support for optimal irrigation

## 📚 Data Sources

The application uses several agricultural datasets:
- Crop production statistics by district
- Irrigation source data by district
- Temperature (max/min) data by district
- Precipitation data by district

## 🧪 Testing

The project includes several test scripts to verify functionality:
- `test_enhanced_commodity_tool.py` - Tests for commodity price tools
- `test_geographies.py` - Tests for geographic data handling
- `test_simple_commodity.py` - Tests for basic commodity queries

Run tests with:
```bash
python -m pytest test_*.py
```

## 🛠️ Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📁 Project Structure

```
hackathon-capital-one/
├── app/                    # Main application modules
│   ├── modules/            # Core functionality
│   │   ├── tools/          # Individual tool implementations
│   │   ├── ui/             # User interface components
│   │   ├── api.py          # API integrations
│   │   └── prompts.py      # System prompts
│   └── config.py           # Application configuration
├── data/                   # Agricultural datasets and loaders
├── docs/                   # Documentation files
├── logs/                   # Application logs
├── tests/                  # Test scripts
├── streamlit_app.py        # Main Streamlit application
├── requirements.txt        # Python dependencies
└── .env.example            # Environment variable template
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.