import aiohttp
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .config import Config

logger = logging.getLogger(__name__)

async def get_weather_by_coords(lat: float, lon: float) -> Dict:
    """
    Get current weather and 3-day forecast by coordinates
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Dictionary with current weather and forecast data
    """
    try:
        if not Config.WEATHER_API_KEY:
            return {
                "error": "Weather API key not configured",
                "current": None,
                "forecast": None
            }
        
        async with aiohttp.ClientSession() as session:
            # Get current weather
            current_url = f"{Config.WEATHER_BASE_URL}/current.json"
            current_params = {
                "key": Config.WEATHER_API_KEY,
                "q": f"{lat},{lon}",
                "aqi": "no"
            }
            
            async with session.get(current_url, params=current_params) as response:
                if response.status == 200:
                    current_data = await response.json()
                else:
                    current_data = {"error": f"Weather API error: {response.status}"}
            
            # Get 3-day forecast
            forecast_url = f"{Config.WEATHER_BASE_URL}/forecast.json"
            forecast_params = {
                "key": Config.WEATHER_API_KEY,
                "q": f"{lat},{lon}",
                "days": 3,
                "aqi": "no",
                "alerts": "no"
            }
            
            async with session.get(forecast_url, params=forecast_params) as response:
                if response.status == 200:
                    forecast_data = await response.json()
                else:
                    forecast_data = {"error": f"Forecast API error: {response.status}"}
            
            return {
                "current": current_data,
                "forecast": forecast_data,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return {
            "error": f"Weather service error: {str(e)}",
            "current": None,
            "forecast": None
        }

async def search_agricultural_knowledge(query: str, crop_type: str = None, location: str = None) -> str:
    """
    Search agricultural knowledge using Exa.AI
    
    Args:
        query: Search query
        crop_type: Type of crop (optional)
        location: Location context (optional)
        
    Returns:
        Search results as string
    """
    try:
        if not Config.EXA_API_KEY:
            return f"Mock agricultural knowledge for: {query}. Crop: {crop_type}, Location: {location}"
        
        # Build search query with agricultural context
        search_query = f"agriculture farming {query}"
        if crop_type:
            search_query += f" {crop_type}"
        if location:
            search_query += f" {location}"
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {Config.EXA_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "query": search_query,
                "numResults": 5,
                "includeDomains": ["extension.org", "usda.gov", "fao.org", "agriculture.com"],
                "useAutoprompt": True
            }
            
            async with session.post(
                f"{Config.EXA_BASE_URL}/search",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract and format results
                    results = []
                    for result in data.get("results", []):
                        title = result.get("title", "")
                        text = result.get("text", "")
                        url = result.get("url", "")
                        
                        results.append(f"Title: {title}\nContent: {text[:300]}...\nSource: {url}\n")
                    
                    return "\n".join(results) if results else "No relevant agricultural information found."
                else:
                    return f"Exa.AI search error: {response.status}"
                    
    except Exception as e:
        logger.error(f"Agricultural knowledge search error: {e}")
        return f"Search service error: {str(e)}"

async def calculate_irrigation_schedule(crop_type: str, weather_data: Dict, soil_type: str = "medium") -> str:
    """
    Calculate irrigation recommendations based on crop and weather
    
    Args:
        crop_type: Type of crop
        weather_data: Weather information
        soil_type: Soil type (light/medium/heavy)
        
    Returns:
        Irrigation recommendations
    """
    try:
        # Extract weather information
        current_temp = weather_data.get("current", {}).get("current", {}).get("temp_c", 25)
        humidity = weather_data.get("current", {}).get("current", {}).get("humidity", 60)
        
        # Basic irrigation logic (simplified for prototype)
        crop_water_needs = {
            "wheat": {"frequency": "3-4 days", "amount": "1-2 inches"},
            "rice": {"frequency": "daily", "amount": "2-3 inches"},
            "corn": {"frequency": "2-3 days", "amount": "1.5-2 inches"},
            "tomato": {"frequency": "2-3 days", "amount": "1-1.5 inches"},
            "potato": {"frequency": "3-4 days", "amount": "1-2 inches"}
        }
        
        crop_info = crop_water_needs.get(crop_type.lower(), {"frequency": "3-4 days", "amount": "1-2 inches"})
        
        # Adjust based on weather
        if current_temp > 30:
            frequency = "daily"
            amount = crop_info["amount"]
        elif current_temp < 15:
            frequency = "5-6 days"
            amount = crop_info["amount"]
        else:
            frequency = crop_info["frequency"]
            amount = crop_info["amount"]
        
        # Adjust for soil type
        if soil_type == "light":
            amount = f"{amount} (sandy soil - more frequent)"
        elif soil_type == "heavy":
            amount = f"{amount} (clay soil - less frequent)"
        
        return f"Irrigation Schedule for {crop_type}:\n- Frequency: {frequency}\n- Amount: {amount}\n- Current conditions: {current_temp}°C, {humidity}% humidity"
        
    except Exception as e:
        logger.error(f"Irrigation calculation error: {e}")
        return f"Error calculating irrigation: {str(e)}"

async def pest_identification_guide(symptoms: str, crop_type: str = None) -> str:
    """
    Provide pest identification and control guidance
    
    Args:
        symptoms: Description of plant symptoms
        crop_type: Type of crop affected
        
    Returns:
        Pest identification and control advice
    """
    try:
        # Simplified pest identification (in production, use ML models)
        common_pests = {
            "yellow leaves": "Possible causes: nutrient deficiency, overwatering, or aphid infestation",
            "holes in leaves": "Possible causes: caterpillars, beetles, or slugs",
            "white spots": "Possible causes: powdery mildew, spider mites, or scale insects",
            "wilting": "Possible causes: root rot, drought stress, or bacterial wilt"
        }
        
        # Find matching symptoms
        advice = []
        for symptom, cause in common_pests.items():
            if symptom.lower() in symptoms.lower():
                advice.append(cause)
        
        if not advice:
            advice.append("General advice: Monitor plant health, check for pests regularly, and maintain proper soil conditions")
        
        return f"Pest Identification for {crop_type or 'your crop'}:\n" + "\n".join(f"- {item}" for item in advice)
        
    except Exception as e:
        logger.error(f"Pest identification error: {e}")
        return f"Error in pest identification: {str(e)}"

async def fertilizer_recommendations(crop_type: str, soil_ph: float = 6.5, growth_stage: str = "vegetative") -> str:
    """
    Provide fertilizer recommendations
    
    Args:
        crop_type: Type of crop
        soil_ph: Soil pH level
        growth_stage: Current growth stage
        
    Returns:
        Fertilizer recommendations
    """
    try:
        # Basic fertilizer recommendations (simplified)
        crop_fertilizers = {
            "wheat": {"npk": "10-20-20", "frequency": "at planting and tillering"},
            "rice": {"npk": "12-24-12", "frequency": "at transplanting and panicle initiation"},
            "corn": {"npk": "15-15-15", "frequency": "at planting and knee-high stage"},
            "tomato": {"npk": "5-10-10", "frequency": "at planting and flowering"},
            "potato": {"npk": "10-20-20", "frequency": "at planting and hilling"}
        }
        
        crop_info = crop_fertilizers.get(crop_type.lower(), {"npk": "10-10-10", "frequency": "at planting"})
        
        # Adjust for soil pH
        ph_advice = ""
        if soil_ph < 6.0:
            ph_advice = "Consider adding lime to raise soil pH."
        elif soil_ph > 7.5:
            ph_advice = "Consider adding sulfur to lower soil pH."
        
        return f"Fertilizer Recommendations for {crop_type}:\n- NPK Ratio: {crop_info['npk']}\n- Application: {crop_info['frequency']}\n- Soil pH: {soil_ph} {ph_advice}"
        
    except Exception as e:
        logger.error(f"Fertilizer recommendation error: {e}")
        return f"Error in fertilizer recommendations: {str(e)}"

async def math_operations(operation: str, numbers: List[float]) -> str:
    """
    Perform basic mathematical operations
    
    Args:
        operation: Type of operation (add, subtract, multiply, divide, average)
        numbers: List of numbers to operate on
        
    Returns:
        Result of the mathematical operation
    """
    try:
        if not numbers:
            return "Error: No numbers provided for calculation"
        
        if operation.lower() == "add":
            result = sum(numbers)
            return f"Sum of {numbers} = {result}"
        
        elif operation.lower() == "subtract":
            if len(numbers) < 2:
                return "Error: Need at least 2 numbers for subtraction"
            result = numbers[0] - sum(numbers[1:])
            return f"Subtraction: {numbers[0]} - {sum(numbers[1:])} = {result}"
        
        elif operation.lower() == "multiply":
            result = 1
            for num in numbers:
                result *= num
            return f"Product of {numbers} = {result}"
        
        elif operation.lower() == "divide":
            if len(numbers) < 2:
                return "Error: Need at least 2 numbers for division"
            result = numbers[0]
            for num in numbers[1:]:
                if num == 0:
                    return "Error: Cannot divide by zero"
                result /= num
            return f"Division: {numbers[0]} ÷ {numbers[1:]} = {result}"
        
        elif operation.lower() == "average":
            result = sum(numbers) / len(numbers)
            return f"Average of {numbers} = {result}"
        
        elif operation.lower() == "power":
            if len(numbers) < 2:
                return "Error: Need 2 numbers for power operation (base, exponent)"
            result = numbers[0] ** numbers[1]
            return f"Power: {numbers[0]} ^ {numbers[1]} = {result}"
        
        else:
            return f"Error: Unknown operation '{operation}'. Supported operations: add, subtract, multiply, divide, average, power"
            
    except Exception as e:
        logger.error(f"Math operation error: {e}")
        return f"Error in math operation: {str(e)}"

async def simple_calculator(expression: str) -> str:
    """
    Simple calculator for basic arithmetic expressions
    
    Args:
        expression: Mathematical expression as string (e.g., "2 + 3 * 4")
        
    Returns:
        Result of the calculation
    """
    try:
        # Basic safety check - only allow numbers, basic operators, and spaces
        allowed_chars = set("0123456789+-*/.() ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters. Only numbers and basic operators (+, -, *, /, .) are allowed."
        
        # Evaluate the expression
        result = eval(expression)
        return f"Calculation: {expression} = {result}"
        
    except ZeroDivisionError:
        return "Error: Cannot divide by zero"
    except Exception as e:
        logger.error(f"Calculator error: {e}")
        return f"Error in calculation: {str(e)}"

# Tool registry for LangGraph
AGRICULTURAL_TOOLS = {
    "get_weather_by_coords": {
        "function": get_weather_by_coords,
        "description": "Get current weather and 3-day forecast by coordinates",
        "parameters": {
            "lat": "float",
            "lon": "float"
        }
    },
    "search_agricultural_knowledge": {
        "function": search_agricultural_knowledge,
        "description": "Search agricultural knowledge base for farming advice",
        "parameters": {
            "query": "str",
            "crop_type": "str (optional)",
            "location": "str (optional)"
        }
    },
    "calculate_irrigation_schedule": {
        "function": calculate_irrigation_schedule,
        "description": "Calculate irrigation recommendations based on crop and weather",
        "parameters": {
            "crop_type": "str",
            "weather_data": "dict",
            "soil_type": "str (optional)"
        }
    },
    "pest_identification_guide": {
        "function": pest_identification_guide,
        "description": "Identify pests and provide control guidance",
        "parameters": {
            "symptoms": "str",
            "crop_type": "str (optional)"
        }
    },
    "fertilizer_recommendations": {
        "function": fertilizer_recommendations,
        "description": "Provide fertilizer recommendations based on crop and soil",
        "parameters": {
            "crop_type": "str",
            "soil_ph": "float (optional)",
            "growth_stage": "str (optional)"
        }
    },
    "math_operations": {
        "function": math_operations,
        "description": "Perform basic mathematical operations (add, subtract, multiply, divide, average, power)",
        "parameters": {
            "operation": "str",
            "numbers": "List[float]"
        }
    },
    "simple_calculator": {
        "function": simple_calculator,
        "description": "Simple calculator for basic arithmetic expressions",
        "parameters": {
            "expression": "str"
        }
    }
} 