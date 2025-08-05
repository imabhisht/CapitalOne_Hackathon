from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from typing import TypedDict, List, Optional, Literal
import json
from datetime import datetime

# ============================================================================
# STATE DEFINITIONS
# ============================================================================

class AgentState(TypedDict):
    """State for the main agricultural advisor agent"""
    messages: List[dict]
    user_query: str
    crop_type: Optional[str]
    location: Optional[str]
    season: Optional[str]
    issue_type: Optional[str]  # irrigation, pest, disease, fertilizer
    rag_context: Optional[str]
    final_response: Optional[str]
    needs_more_info: bool

class UserInfoState(TypedDict):
    """State for user information gathering agent"""
    messages: List[dict]
    user_profile: dict
    required_fields: List[str]
    collected_fields: List[str]
    current_question: Optional[str]
    ready_for_main_agent: bool

# ============================================================================
# MOCK FUNCTIONS (Assume these exist)
# ============================================================================

def save_chat_message(session_id: str, message: dict):
    """Mock function to save message to MongoDB"""
    pass

def get_chat_history(session_id: str) -> List[dict]:
    """Mock function to retrieve chat history from MongoDB"""
    return []

def rag_search(query: str, context: dict) -> str:
    """Mock RAG function - returns agricultural advice"""
    return f"Based on your query about {query}, here's agricultural advice..."

def get_weather_data(location: str) -> dict:
    """Mock function to get weather data"""
    return {"temperature": 25, "humidity": 60, "forecast": "sunny"}

# ============================================================================
# TOOLS
# ============================================================================

@tool
def search_agricultural_knowledge(query: str, crop_type: str = None, location: str = None) -> str:
    """Search agricultural knowledge base for advice"""
    context = {
        "crop_type": crop_type,
        "location": location,
        "query": query
    }
    return rag_search(query, context)

@tool
def get_weather_info(location: str) -> str:
    """Get current weather information"""
    weather = get_weather_data(location)
    return json.dumps(weather)

@tool
def irrigation_calculator(crop_type: str, weather_data: dict, soil_type: str = "medium") -> str:
    """Calculate irrigation recommendations"""
    return f"For {crop_type} in current weather, irrigate every 3-4 days with 2-3 inches of water"

# ============================================================================
# MAIN AGRICULTURAL ADVISOR AGENT
# ============================================================================

def analyze_query(state: AgentState) -> AgentState:
    """Analyze user query and extract relevant information"""
    query = state["user_query"].lower()
    
    # Simple keyword extraction (in reality, use NLP)
    crop_keywords = ["wheat", "rice", "corn", "tomato", "potato", "cabbage"]
    issue_keywords = {
        "irrigation": ["water", "irrigate", "irrigation", "watering"],
        "pest": ["pest", "insect", "bug", "aphid"],
        "disease": ["disease", "fungus", "rot", "blight"],
        "fertilizer": ["fertilizer", "nutrient", "nitrogen", "phosphorus"]
    }
    
    # Extract crop type
    crop_type = None
    for crop in crop_keywords:
        if crop in query:
            crop_type = crop
            break
    
    # Extract issue type
    issue_type = None
    for issue, keywords in issue_keywords.items():
        if any(keyword in query for keyword in keywords):
            issue_type = issue
            break
    
    state.update({
        "crop_type": crop_type,
        "issue_type": issue_type,
        "needs_more_info": not (crop_type and issue_type)
    })
    
    return state

def check_information_completeness(state: AgentState) -> AgentState:
    """Check if we have enough information to provide advice"""
    required_info = ["crop_type", "issue_type"]
    missing_info = []
    
    for info in required_info:
        if not state.get(info):
            missing_info.append(info)
    
    if missing_info:
        state["needs_more_info"] = True
        # Generate follow-up questions
        question = f"I need more information. What crop are you asking about?"
        if state.get("crop_type") and not state.get("issue_type"):
            question = "What specific issue are you facing? (irrigation, pest control, disease, or fertilization)"
        
        state["messages"].append({
            "role": "assistant",
            "content": question,
            "timestamp": datetime.now().isoformat()
        })
    else:
        state["needs_more_info"] = False
    
    return state

def retrieve_agricultural_data(state: AgentState) -> AgentState:
    """Retrieve relevant agricultural data using RAG"""
    if state["needs_more_info"]:
        return state
    
    query = f"{state['issue_type']} advice for {state['crop_type']}"
    context = {
        "crop_type": state["crop_type"],
        "location": state.get("location"),
        "issue_type": state["issue_type"]
    }
    
    rag_context = rag_search(query, context)
    state["rag_context"] = rag_context
    
    return state

def generate_advice(state: AgentState) -> AgentState:
    """Generate final agricultural advice"""
    if state["needs_more_info"]:
        return state
    
    # Combine RAG context with current conditions
    advice_parts = []
    
    if state["rag_context"]:
        advice_parts.append(f"Agricultural Knowledge: {state['rag_context']}")
    
    if state.get("location"):
        weather_info = get_weather_info(state["location"])
        advice_parts.append(f"Weather Considerations: {weather_info}")
    
    if state["issue_type"] == "irrigation":
        irrigation_advice = irrigation_calculator(
            state["crop_type"], 
            get_weather_data(state.get("location", "default"))
        )
        advice_parts.append(f"Irrigation Schedule: {irrigation_advice}")
    
    final_response = "\n\n".join(advice_parts)
    state["final_response"] = final_response
    
    # Add to messages
    state["messages"].append({
        "role": "assistant",
        "content": final_response,
        "timestamp": datetime.now().isoformat()
    })
    
    return state

def route_decision(state: AgentState) -> Literal["ask_more_info", "provide_advice", "end"]:
    """Route based on information completeness"""
    if state["needs_more_info"]:
        return "ask_more_info"
    elif state.get("final_response"):
        return "end"
    else:
        return "provide_advice"

# Build the main agent graph
def create_agricultural_advisor_agent():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("analyze_query", analyze_query)
    workflow.add_node("check_completeness", check_information_completeness)
    workflow.add_node("retrieve_data", retrieve_agricultural_data)
    workflow.add_node("generate_advice", generate_advice)
    
    # Add edges
    workflow.set_entry_point("analyze_query")
    workflow.add_edge("analyze_query", "check_completeness")
    
    # Conditional routing
    workflow.add_conditional_edges(
        "check_completeness",
        route_decision,
        {
            "ask_more_info": END,  # Return to user for more info
            "provide_advice": "retrieve_data",
            "end": END
        }
    )
    
    workflow.add_edge("retrieve_data", "generate_advice")
    workflow.add_edge("generate_advice", END)
    
    return workflow.compile()

# ============================================================================
# USER INFORMATION GATHERING AGENT
# ============================================================================

def initialize_user_profile(state: UserInfoState) -> UserInfoState:
    """Initialize user profile collection"""
    required_fields = ["name", "location", "farm_size", "primary_crops", "experience_level"]
    
    state.update({
        "required_fields": required_fields,
        "collected_fields": [],
        "user_profile": {},
        "ready_for_main_agent": False
    })
    
    return state

def ask_next_question(state: UserInfoState) -> UserInfoState:
    """Ask the next required question"""
    remaining_fields = [f for f in state["required_fields"] if f not in state["collected_fields"]]
    
    if not remaining_fields:
        state["ready_for_main_agent"] = True
        state["current_question"] = None
        return state
    
    next_field = remaining_fields[0]
    questions = {
        "name": "What's your name?",
        "location": "What's your farm location (city/district)?",
        "farm_size": "What's your farm size (in acres)?",
        "primary_crops": "What are your primary crops?",
        "experience_level": "What's your farming experience level? (beginner/intermediate/expert)"
    }
    
    question = questions.get(next_field, f"Please provide your {next_field}")
    state["current_question"] = question
    
    # Add question to messages
    state["messages"].append({
        "role": "assistant",
        "content": question,
        "timestamp": datetime.now().isoformat()
    })
    
    return state

def process_user_response(state: UserInfoState) -> UserInfoState:
    """Process user's response to current question"""
    if not state["messages"]:
        return state
    
    last_message = state["messages"][-1]
    if last_message["role"] != "user":
        return state
    
    user_response = last_message["content"]
    remaining_fields = [f for f in state["required_fields"] if f not in state["collected_fields"]]
    
    if remaining_fields:
        current_field = remaining_fields[0]
        state["user_profile"][current_field] = user_response
        state["collected_fields"].append(current_field)
    
    return state

def check_profile_completeness(state: UserInfoState) -> Literal["ask_question", "complete", "process_response"]:
    """Check if user profile is complete"""
    if len(state["collected_fields"]) >= len(state["required_fields"]):
        return "complete"
    elif state.get("current_question"):
        return "process_response"
    else:
        return "ask_question"

def complete_profile_setup(state: UserInfoState) -> UserInfoState:
    """Complete the profile setup"""
    state["ready_for_main_agent"] = True
    
    summary = f"Great! I have your information:\n"
    for field, value in state["user_profile"].items():
        summary += f"- {field.replace('_', ' ').title()}: {value}\n"
    summary += "\nNow you can ask me any agricultural questions!"
    
    state["messages"].append({
        "role": "assistant",
        "content": summary,
        "timestamp": datetime.now().isoformat()
    })
    
    return state

# Build the user info agent graph
def create_user_info_agent():
    workflow = StateGraph(UserInfoState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_user_profile)
    workflow.add_node("ask_question", ask_next_question)
    workflow.add_node("process_response", process_user_response)
    workflow.add_node("complete_setup", complete_profile_setup)
    
    # Add edges
    workflow.set_entry_point("initialize")
    workflow.add_edge("initialize", "ask_question")
    
    # Conditional routing
    workflow.add_conditional_edges(
        "ask_question",
        check_profile_completeness,
        {
            "ask_question": "ask_question",
            "complete": "complete_setup",
            "process_response": "process_response"
        }
    )
    
    workflow.add_edge("process_response", "ask_question")
    workflow.add_edge("complete_setup", END)
    
    return workflow.compile()

# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

class AgriculturalAdvisorSystem:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.user_info_agent = create_user_info_agent()
        self.advisor_agent = create_agricultural_advisor_agent()
        self.user_profile_complete = False
        
    def process_message(self, user_message: str) -> str:
        """Process incoming user message"""
        # Save user message to MongoDB
        save_chat_message(self.session_id, {
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        if not self.user_profile_complete:
            # Use user info gathering agent
            state = UserInfoState(
                messages=[{"role": "user", "content": user_message}],
                user_profile={},
                required_fields=[],
                collected_fields=[],
                current_question=None,
                ready_for_main_agent=False
            )
            
            result = self.user_info_agent.invoke(state)
            
            if result["ready_for_main_agent"]:
                self.user_profile_complete = True
            
            # Save assistant response
            if result["messages"]:
                last_response = result["messages"][-1]
                if last_response["role"] == "assistant":
                    save_chat_message(self.session_id, last_response)
                    return last_response["content"]
        
        else:
            # Use main agricultural advisor agent
            state = AgentState(
                messages=[{"role": "user", "content": user_message}],
                user_query=user_message,
                crop_type=None,
                location=None,
                season=None,
                issue_type=None,
                rag_context=None,
                final_response=None,
                needs_more_info=False
            )
            
            result = self.advisor_agent.invoke(state)
            
            # Save assistant response
            if result["messages"]:
                last_response = result["messages"][-1]
                if last_response["role"] == "assistant":
                    save_chat_message(self.session_id, last_response)
                    return last_response["content"]
        
        return "I'm sorry, I couldn't process your message. Please try again."

# ============================================================================
# USAGE EXAMPLE
# ============================================================================

def main():
    # Create system instance
    advisor_system = AgriculturalAdvisorSystem("user_session_123")
    
    # Simulate conversation flow
    print("=== User Info Gathering Phase ===")
    response1 = advisor_system.process_message("Hi, I need help with my farm")
    print(f"Bot: {response1}")
    
    response2 = advisor_system.process_message("John Farmer")
    print(f"Bot: {response2}")
    
    response3 = advisor_system.process_message("Punjab, India")
    print(f"Bot: {response3}")
    
    response4 = advisor_system.process_message("5 acres")
    print(f"Bot: {response4}")
    
    response5 = advisor_system.process_message("Wheat and Rice")
    print(f"Bot: {response5}")
    
    response6 = advisor_system.process_message("Intermediate")
    print(f"Bot: {response6}")
    
    print("\n=== Agricultural Advice Phase ===")
    response7 = advisor_system.process_message("When should I irrigate my wheat crop?")
    print(f"Bot: {response7}")
    
    response8 = advisor_system.process_message("My tomato plants have yellow leaves")
    print(f"Bot: {response8}")

if __name__ == "__main__":
    main()