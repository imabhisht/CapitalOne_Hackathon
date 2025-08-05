from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from typing import TypedDict, List, Optional, Literal, Dict, Any
import json
import logging
from datetime import datetime
import asyncio

from .config import Config
from .database import chat_storage
from .llm_client import gemini_client
from .tools import AGRICULTURAL_TOOLS

logger = logging.getLogger(__name__)

# ============================================================================
# STATE DEFINITIONS
# ============================================================================

class AgentState(TypedDict):
    """State for the agricultural advisor agent"""
    messages: List[Dict[str, Any]]
    user_query: str
    session_id: str
    crop_type: Optional[str]
    location: Optional[str]
    coordinates: Optional[Dict[str, float]]  # lat, lon
    issue_type: Optional[str]  # irrigation, pest, disease, fertilizer, weather
    weather_data: Optional[Dict]
    agricultural_knowledge: Optional[str]
    tool_results: Dict[str, Any]
    final_response: Optional[str]
    needs_more_info: bool
    error_message: Optional[str]
    is_general_query: bool
    is_math_query: bool

# ============================================================================
# TOOL DEFINITIONS FOR LANGGRAPH
# ============================================================================

@tool
async def tool_get_weather_by_coords(lat: float, lon: float) -> str:
    """Get current weather and 3-day forecast by coordinates"""
    from .tools import get_weather_by_coords
    result = await get_weather_by_coords(lat, lon)
    return json.dumps(result, default=str)

@tool
async def tool_search_agricultural_knowledge(query: str, crop_type: str = None, location: str = None) -> str:
    """Search agricultural knowledge base for farming advice"""
    from .tools import search_agricultural_knowledge
    result = await search_agricultural_knowledge(query, crop_type, location)
    return result

@tool
async def tool_calculate_irrigation_schedule(crop_type: str, weather_data: str, soil_type: str = "medium") -> str:
    """Calculate irrigation recommendations based on crop and weather"""
    from .tools import calculate_irrigation_schedule
    weather_dict = json.loads(weather_data) if isinstance(weather_data, str) else weather_data
    result = await calculate_irrigation_schedule(crop_type, weather_dict, soil_type)
    return result

@tool
async def tool_pest_identification_guide(symptoms: str, crop_type: str = None) -> str:
    """Identify pests and provide control guidance"""
    from .tools import pest_identification_guide
    result = await pest_identification_guide(symptoms, crop_type)
    return result

@tool
async def tool_fertilizer_recommendations(crop_type: str, soil_ph: float = 6.5, growth_stage: str = "vegetative") -> str:
    """Provide fertilizer recommendations based on crop and soil"""
    from .tools import fertilizer_recommendations
    result = await fertilizer_recommendations(crop_type, soil_ph, growth_stage)
    return result

@tool
async def tool_math_operations(operation: str, numbers: str) -> str:
    """Perform basic mathematical operations"""
    from .tools import math_operations
    import ast
    # Convert string representation of list to actual list
    try:
        numbers_list = ast.literal_eval(numbers)
        result = await math_operations(operation, numbers_list)
        return result
    except Exception as e:
        return f"Error parsing numbers: {str(e)}"

@tool
async def tool_simple_calculator(expression: str) -> str:
    """Simple calculator for basic arithmetic expressions"""
    from .tools import simple_calculator
    result = await simple_calculator(expression)
    return result

# ============================================================================
# AGENT NODES
# ============================================================================

def analyze_query(state: AgentState) -> AgentState:
    """Analyze user query and extract relevant information"""
    query = state["user_query"].lower()
    
    # Check if this is a math query first
    math_keywords = ["calculate", "what is", "math", "add", "subtract", "multiply", "divide", "sum", "average", "power", "+", "-", "*", "/", "="]
    is_math_query = any(keyword in query for keyword in math_keywords) or any(char in query for char in "+-*/=")
    
    if is_math_query:
        state.update({
            "crop_type": None,
            "issue_type": None,
            "location": None,
            "needs_more_info": False,
            "is_general_query": True,
            "is_math_query": True,
            "tool_results": {}
        })
        return state
    
    # Extract crop type
    crop_keywords = ["wheat", "rice", "corn", "maize", "tomato", "potato", "cabbage", "lettuce", "carrot", "onion"]
    crop_type = None
    for crop in crop_keywords:
        if crop in query:
            crop_type = crop
            break
    
    # Extract issue type
    issue_keywords = {
        "irrigation": ["water", "irrigate", "irrigation", "watering", "drought", "moisture"],
        "pest": ["pest", "insect", "bug", "aphid", "caterpillar", "beetle", "damage"],
        "disease": ["disease", "fungus", "rot", "blight", "mildew", "infection"],
        "fertilizer": ["fertilizer", "nutrient", "nitrogen", "phosphorus", "potassium", "npk"],
        "weather": ["weather", "temperature", "rain", "forecast", "climate"]
    }
    
    issue_type = None
    for issue, keywords in issue_keywords.items():
        if any(keyword in query for keyword in keywords):
            issue_type = issue
            break
    
    # Extract location hints
    location_keywords = ["in", "at", "near", "around"]
    location = None
    words = query.split()
    for i, word in enumerate(words):
        if word in location_keywords and i + 1 < len(words):
            location = " ".join(words[i+1:i+3])  # Take next 2 words as location
            break
    
    # Check if this is a general query (greeting, general question, etc.)
    general_keywords = ["hello", "hi", "hey", "how are you", "what can you do", "help", "joke", "weather"]
    is_general_query = any(keyword in query for keyword in general_keywords)
    
    # Only require crop_type and issue_type for specific agricultural queries
    needs_agricultural_info = crop_type is not None or issue_type is not None or any(ag_keyword in query for ag_keyword in ["farm", "agriculture", "crop", "plant", "soil"])
    
    state.update({
        "crop_type": crop_type,
        "issue_type": issue_type,
        "location": location,
        "needs_more_info": needs_agricultural_info and not (crop_type and issue_type),
        "is_general_query": is_general_query,
        "is_math_query": False,
        "tool_results": {}
    })
    
    return state

def check_information_completeness(state: AgentState) -> AgentState:
    """Check if we have enough information to provide advice"""
    
    # If it's a general query, don't ask for more information
    if state.get("is_general_query", False):
        state["needs_more_info"] = False
        return state
    
    # For agricultural queries, check if we have enough information
    required_info = ["crop_type", "issue_type"]
    missing_info = []
    
    for info in required_info:
        if not state.get(info):
            missing_info.append(info)
    
    if missing_info:
        state["needs_more_info"] = True
        question = "I need more information to help you effectively. "
        
        if not state.get("crop_type"):
            question += "What crop are you asking about? (e.g., wheat, rice, tomato, potato)"
        elif not state.get("issue_type"):
            question += "What specific issue are you facing? (irrigation, pest control, disease, fertilization, or weather)"
        
        state["messages"].append({
            "role": "assistant",
            "content": question,
            "timestamp": datetime.now().isoformat()
        })
    else:
        state["needs_more_info"] = False
    
    return state

async def retrieve_weather_data(state: AgentState) -> AgentState:
    """Retrieve weather data if coordinates are available"""
    if state["needs_more_info"] or not state.get("coordinates"):
        return state
    
    try:
        # Use default coordinates if not provided (for prototype)
        lat = state["coordinates"].get("lat", 40.7128)  # Default to NYC
        lon = state["coordinates"].get("lon", -74.0060)
        
        # Call the tool function directly instead of using the tool decorator
        from .tools import get_weather_by_coords
        weather_result = await get_weather_by_coords(lat, lon)
        state["weather_data"] = weather_result
        state["tool_results"]["weather"] = json.dumps(weather_result, default=str)
        
    except Exception as e:
        logger.error(f"Weather retrieval error: {e}")
        state["error_message"] = f"Weather data error: {str(e)}"
    
    return state

async def retrieve_agricultural_knowledge(state: AgentState) -> AgentState:
    """Retrieve agricultural knowledge using Exa.AI"""
    if state["needs_more_info"]:
        return state
    
    try:
        query = f"{state['issue_type']} advice for {state['crop_type']}"
        # Call the tool function directly instead of using the tool decorator
        from .tools import search_agricultural_knowledge
        knowledge_result = await search_agricultural_knowledge(
            query, 
            state.get("crop_type"), 
            state.get("location")
        )
        
        state["agricultural_knowledge"] = knowledge_result
        state["tool_results"]["knowledge"] = knowledge_result
        
    except Exception as e:
        logger.error(f"Knowledge retrieval error: {e}")
        state["error_message"] = f"Knowledge search error: {str(e)}"
    
    return state

async def generate_specialized_advice(state: AgentState) -> AgentState:
    """Generate specialized advice based on issue type"""
    if state["needs_more_info"]:
        return state
    
    try:
        issue_type = state["issue_type"]
        crop_type = state["crop_type"]
        
        if issue_type == "irrigation" and state.get("weather_data"):
            # Call the tool function directly
            from .tools import calculate_irrigation_schedule
            irrigation_result = await calculate_irrigation_schedule(
                crop_type, 
                state["weather_data"], 
                "medium"
            )
            state["tool_results"]["irrigation"] = irrigation_result
            
        elif issue_type == "pest":
            # Extract symptoms from user query
            symptoms = state["user_query"]
            # Call the tool function directly
            from .tools import pest_identification_guide
            pest_result = await pest_identification_guide(symptoms, crop_type)
            state["tool_results"]["pest"] = pest_result
            
        elif issue_type == "fertilizer":
            # Call the tool function directly
            from .tools import fertilizer_recommendations
            fertilizer_result = await fertilizer_recommendations(crop_type)
            state["tool_results"]["fertilizer"] = fertilizer_result
            
    except Exception as e:
        logger.error(f"Specialized advice error: {e}")
        state["error_message"] = f"Advice generation error: {str(e)}"
    
    return state

async def generate_final_response(state: AgentState) -> AgentState:
    """Generate final comprehensive response using Gemini"""
    if state["needs_more_info"]:
        return state
    
    try:
        # Handle math queries
        if state.get("is_math_query", False):
            query = state["user_query"].lower()
            
            # Try to extract numbers and operation from the query
            import re
            
            # Look for simple arithmetic expressions
            if any(op in query for op in ["+", "-", "*", "/"]):
                # Extract the mathematical expression
                expression_match = re.search(r'(\d+(?:\s*[+\-*/]\s*\d+)+)', query)
                if expression_match:
                    expression = expression_match.group(1)
                    # Clean up the expression
                    expression = re.sub(r'\s+', '', expression)  # Remove spaces
                    # Call the tool function directly
                    from .tools import simple_calculator
                    result = await simple_calculator(expression)
                    state["final_response"] = result
                else:
                    state["final_response"] = "I can help with math calculations. Please provide a clear expression like '2 + 3' or '5 * 4'."
            else:
                # Try to extract operation and numbers
                numbers = re.findall(r'\d+', query)
                if numbers:
                    numbers = [float(n) for n in numbers]
                    
                    # Call the tool function directly
                    from .tools import math_operations
                    
                    if "add" in query or "sum" in query or "plus" in query:
                        result = await math_operations("add", numbers)
                    elif "subtract" in query or "minus" in query:
                        result = await math_operations("subtract", numbers)
                    elif "multiply" in query or "times" in query:
                        result = await math_operations("multiply", numbers)
                    elif "divide" in query:
                        result = await math_operations("divide", numbers)
                    elif "average" in query or "mean" in query:
                        result = await math_operations("average", numbers)
                    elif "power" in query or "to the power" in query:
                        result = await math_operations("power", numbers)
                    else:
                        # Default to addition for simple number queries
                        result = await math_operations("add", numbers)
                    
                    state["final_response"] = result
                else:
                    state["final_response"] = "I can help with math calculations. Please provide numbers and specify the operation (add, subtract, multiply, divide, average, power)."
            
            # Add to messages
            state["messages"].append({
                "role": "assistant",
                "content": state["final_response"],
                "timestamp": datetime.now().isoformat()
            })
            
            return state
        
        # Handle general queries differently
        if state.get("is_general_query", False):
            # For general queries, provide a friendly introduction
            general_responses = {
                "hello": "Hello! I'm your Agricultural AI Advisor. I can help you with farming questions, crop management, pest control, irrigation, and weather-related advice. How can I assist you with your agricultural needs today?",
                "hi": "Hi there! I'm your Agricultural AI Advisor. I specialize in helping farmers with crop management, pest control, irrigation scheduling, and agricultural advice. What would you like to know about farming?",
                "hey": "Hey! I'm your Agricultural AI Advisor. I'm here to help you with all things farming - from crop selection to pest management to weather advice. What can I help you with today?",
                "how are you": "I'm doing great, thank you for asking! I'm your Agricultural AI Advisor, ready to help you with farming questions, crop management, pest control, and agricultural advice. How can I assist you today?",
                "what can you do": "I'm an Agricultural AI Advisor with expertise in crop management, pest control, irrigation scheduling, fertilizer recommendations, and weather analysis. I can help you with farming questions, provide agricultural advice, and assist with farm planning. What specific farming topic would you like to discuss?",
                "help": "I'm here to help! As your Agricultural AI Advisor, I can assist with crop management, pest identification, irrigation scheduling, fertilizer recommendations, weather analysis, and general farming advice. What do you need help with?",
                "weather": "I can help you with weather information and how it affects your crops! I can provide current weather data, forecasts, and agricultural weather advice. Would you like me to check the weather for your location?",
                "joke": "Here's a farming joke for you: Why did the scarecrow win an award? Because he was outstanding in his field! 😄 As your Agricultural AI Advisor, I'm here to help with farming questions and agricultural advice. What can I assist you with today?"
            }
            
            query_lower = state["user_query"].lower()
            response = None
            
            for keyword, general_response in general_responses.items():
                if keyword in query_lower:
                    response = general_response
                    break
            
            if not response:
                response = "Hello! I'm your Agricultural AI Advisor. I can help you with farming questions, crop management, pest control, irrigation, and agricultural advice. How can I assist you today?"
            
            state["final_response"] = response
            
            # Add to messages
            state["messages"].append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            return state
        
        # For agricultural queries, use the existing logic
        # Prepare context for LLM
        context_parts = []
        
        if state.get("agricultural_knowledge"):
            context_parts.append(f"Agricultural Knowledge: {state['agricultural_knowledge']}")
        
        if state.get("weather_data"):
            weather_summary = f"Weather: {state['weather_data'].get('current', {}).get('current', {}).get('temp_c', 'N/A')}°C"
            context_parts.append(weather_summary)
        
        # Add tool results
        for tool_name, result in state["tool_results"].items():
            if tool_name not in ["weather", "knowledge"]:
                context_parts.append(f"{tool_name.title()} Advice: {result}")
        
        context = "\n\n".join(context_parts)
        
        # Prepare messages for Gemini
        system_message = {
            "role": "system",
            "content": """You are an expert agricultural advisor. Provide clear, practical advice based on the context provided. 
            Be concise but comprehensive. Focus on actionable recommendations."""
        }
        
        user_message = {
            "role": "user",
            "content": f"User Query: {state['user_query']}\n\nContext: {context}\n\nPlease provide agricultural advice."
        }
        
        messages = [system_message, user_message]
        
        # Generate response using Gemini
        final_response = await gemini_client.generate_complete_response(messages)
        state["final_response"] = final_response
        
        # Add to messages
        state["messages"].append({
            "role": "assistant",
            "content": final_response,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Final response generation error: {e}")
        state["error_message"] = f"Response generation error: {str(e)}"
        state["final_response"] = "I apologize, but I encountered an error generating your response. Please try again."
    
    return state

def route_decision(state: AgentState) -> Literal["ask_more_info", "process_query", "end"]:
    """Route based on information completeness"""
    if state["needs_more_info"]:
        return "ask_more_info"
    elif state.get("final_response"):
        return "end"
    else:
        return "process_query"

# ============================================================================
# AGENT GRAPH CONSTRUCTION
# ============================================================================

def create_agricultural_advisor_agent():
    """Create the main agricultural advisor agent"""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("analyze_query", analyze_query)
    workflow.add_node("check_completeness", check_information_completeness)
    workflow.add_node("retrieve_weather", retrieve_weather_data)
    workflow.add_node("retrieve_knowledge", retrieve_agricultural_knowledge)
    workflow.add_node("generate_specialized_advice", generate_specialized_advice)
    workflow.add_node("generate_final_response", generate_final_response)
    
    # Add edges
    workflow.set_entry_point("analyze_query")
    workflow.add_edge("analyze_query", "check_completeness")
    
    # Conditional routing
    workflow.add_conditional_edges(
        "check_completeness",
        route_decision,
        {
            "ask_more_info": END,
            "process_query": "retrieve_weather",
            "end": END
        }
    )
    
    workflow.add_edge("retrieve_weather", "retrieve_knowledge")
    workflow.add_edge("retrieve_knowledge", "generate_specialized_advice")
    workflow.add_edge("generate_specialized_advice", "generate_final_response")
    workflow.add_edge("generate_final_response", END)
    
    return workflow.compile()

# ============================================================================
# MAIN AGENT SYSTEM
# ============================================================================

class AgriculturalAdvisorSystem:
    """Main system for agricultural advice"""
    
    def __init__(self):
        self.agent = create_agricultural_advisor_agent()
    
    async def process_message(self, user_message: str, session_id: str, coordinates: Dict[str, float] = None) -> str:
        """Process user message and return response"""
        try:
            # Save user message
            user_msg = {
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            }
            chat_storage.save_message(session_id, user_msg)
            
            # Get chat history
            chat_history = chat_storage.get_chat_history(session_id, limit=10)
            
            # Prepare initial state
            initial_state = AgentState(
                messages=chat_history + [user_msg],
                user_query=user_message,
                session_id=session_id,
                crop_type=None,
                location=None,
                coordinates=coordinates or {"lat": 40.7128, "lon": -74.0060},  # Default coordinates
                issue_type=None,
                weather_data=None,
                agricultural_knowledge=None,
                tool_results={},
                final_response=None,
                needs_more_info=False,
                error_message=None,
                is_general_query=False,
                is_math_query=False
            )
            
            # Run agent
            result = await self.agent.ainvoke(initial_state)
            
            # Save assistant response
            if result.get("final_response"):
                assistant_msg = {
                    "role": "assistant",
                    "content": result["final_response"],
                    "timestamp": datetime.now().isoformat()
                }
                chat_storage.save_message(session_id, assistant_msg)
                return result["final_response"]
            elif result.get("messages"):
                # Find the last assistant message
                for msg in reversed(result["messages"]):
                    if msg["role"] == "assistant":
                        chat_storage.save_message(session_id, msg)
                        return msg["content"]
            
            return "I'm sorry, I couldn't process your request. Please try again."
            
        except Exception as e:
            logger.error(f"Agent processing error: {e}")
            return f"Error processing your request: {str(e)}"
    
    async def generate_streaming_response(
        self, 
        user_message: str, 
        session_id: str, 
        coordinates: Dict[str, float] = None,
        **kwargs
    ):
        """Generate streaming response for the agricultural advisor"""
        try:
            # For streaming, we'll use the complete response and stream it word by word
            complete_response = await self.process_message(user_message, session_id, coordinates)
            
            words = complete_response.split()
            for word in words:
                yield (word + " ", False)
                await asyncio.sleep(Config.STREAMING_DELAY)
            
            yield ("", True)  # Signal completion
            
        except Exception as e:
            logger.error(f"Streaming response error: {e}")
            yield (f"Error: {str(e)}", True)
    
    async def generate_complete_response(
        self, 
        user_message: str, 
        session_id: str, 
        coordinates: Dict[str, float] = None,
        **kwargs
    ) -> str:
        """Generate complete response for the agricultural advisor"""
        return await self.process_message(user_message, session_id, coordinates)

# Global instance
agricultural_system = AgriculturalAdvisorSystem() 