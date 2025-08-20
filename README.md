# **🚀 Krishi Mitra - Agricultural Assistant for Indian Farmers**  
*Now Live! Accessible at [https://krishi-mitra.streamlit.app](https://krishi-mitra.streamlit.app)*

An intelligent, AI-powered agricultural assistant designed to help Indian farmers make data-driven decisions about crops, weather, irrigation, market prices, and soil conditions — all through a simple, natural language interface.

---

## 🌾 Features

- **📍 Location-aware assistance**: Uses browser geolocation to provide hyper-local insights specific to your farm's region
- **🌦️ Enhanced weather forecasts**:
  - Current weather with air quality and atmospheric data
  - 14-day forecasts and hourly predictions
  - Historical weather (since 2010) and weather alerts
- **🌾 Crop guidance**: Recommends suitable crops based on your district’s historical production data
- **💧 Irrigation support**: Provides irrigation source statistics and **satellite-based soil moisture monitoring**
- **📉 Climate trends**: Analyzes long-term temperature and precipitation patterns
- **💵 Real-time market prices**: Fetches commodity prices from the **CEDA Agmarknet API**
- **🤖 AI-powered insights**: Ask questions in plain Hindi or English and get actionable farming advice

---

## 🔗 Live Application
👉 **Visit now**: [https://krishi-mitra.streamlit.app](https://krishi-mitra.streamlit.app)

Experience the power of AI and satellite data for agriculture — no technical setup needed!

---

## 💬 How to Use

Simply ask questions like:
- "Should I irrigate my wheat field today?"
- "What is the 7-day weather forecast for my farm?"
- "Are there any weather warnings in my area?"
- "What are the current market prices for tomatoes in my district?"
- "What crops grow best in Punjab?"
- "Is the soil moisture sufficient in my region?"

The assistant automatically detects your location (with permission) and delivers accurate, timely, and localized responses.

---

## 🛠️ Powered By

| Service | Purpose |
|-------|--------|
| **[OpenRouter](https://openrouter.ai)** | AI model backend for natural language understanding |
| **[WeatherAPI](https://www.weatherapi.com)** | Hyperlocal weather, forecasts, and historical data |
| **[Google Maps API](https://developers.google.com/maps)** | Geocoding and location detection |
| **[CEDA API](https://api.ceda.ashoka.edu.in)** | Real-time agricultural commodity prices |
| **[Planet Labs](https://www.planet.com)** | Satellite-derived **soil water content** data for precision irrigation |

---

## 🌱 Soil Water Content Monitoring

Now integrated with **Planet’s Soil Water Content dataset**, Krishi Mitra provides near-daily, high-resolution soil moisture insights from SMAP and AMSR2 sensors — helping farmers optimize irrigation and conserve water.

Ask:
> "What is the soil moisture level in my field?"  
> "Should I irrigate based on current soil conditions?"

---

## 📚 Data Sources
- District-level crop production, irrigation, and climate data
- CEDA Agmarknet for real-time mandi prices
- Planet’s Planetary Variables for soil moisture
- WeatherAPI for accurate, localized forecasts

---

## 🧪 Tested & Reliable
All core tools are rigorously tested:
- Commodity price fetching
- Geolocation and reverse geocoding
- Weather and soil data integration

Run tests locally with:
```bash
python -m pytest test_*.py
```

---

## 📁 Open Source & Expandable
Built with Streamlit, Python, and MongoDB. Fully modular design for easy contributions and enhancements.

GitHub Repo: `https://github.com/yourusername/krishi-mitra` *(replace with actual link)*

---

## 📝 License
MIT License — free to use, modify, and distribute.

---

**Empowering Indian farmers with AI, satellites, and real-time data.**  
🌍 One app. Infinite fields. Better harvests.  

👉 Try it now: [https://krishi-mitra.streamlit.app](https://krishi-mitra.streamlit.app)
