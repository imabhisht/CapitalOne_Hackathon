import operator
from typing import Annotated, Dict, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import json
import datetime
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# State definition for the multi-agent system
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_intent: Optional[str]
    intent_complete: bool
    task_instructions: Optional[str]
    tool_results: Optional[Dict]
    next_agent: Optional[str]

# Gemini LLM wrapper using OpenAI SDK
class GeminiLLM:
    def __init__(self, model="gemini-2.5-flash", api_key=None):
        """
        Initialize Gemini client using OpenAI SDK format
        
        Args:
            model: Gemini model name (e.g., "gemini-2.5-flash", "gemini-1.5-pro")
            api_key: Gemini API key (if None, will use GEMINI_API_KEY env var)
        """
        self.model = model
        self.client = OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
    
    def invoke(self, messages, temperature=0.7, max_tokens=1000):
        """
        Invoke Gemini with messages
        
        Args:
            messages: List of BaseMessage objects
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
        """
        # Convert LangChain messages to OpenAI format for Gemini
        gemini_messages = []
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                gemini_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                gemini_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                gemini_messages.append({"role": "assistant", "content": msg.content})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=gemini_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            return AIMessage(content=content)
            
        except Exception as e:
            return AIMessage(content=f"Error calling Gemini: {str(e)}")

# Basic tools for the second agent
class WeatherTool(BaseTool):
    name: str = "get_weather"
    description: str = "Get weather information for a location"
    
    def _run(self, location: str) -> str:
        # Mock weather data
        return f"Weather in {location}: 72°F, sunny with light clouds"

class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = "Perform mathematical calculations"
    
    def _run(self, expression: str) -> str:
        try:
            # Simple calculator - in production, use safer evaluation
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error in calculation: {str(e)}"

class SearchTool(BaseTool):
    name: str = "search"
    description: str = "Search for information"
    
    def _run(self, query: str) -> str:
        # Mock search results
        return f"Search results for '{query}': Found relevant information about the topic."

# Agent 1: Intent Gathering Agent
class IntentGatheringAgent:
    def __init__(self, model="gemini-2.5-flash", api_key=None):
        self.llm = GeminiLLM(model=model, api_key=api_key)
        self.system_prompt = """You are an Intent Gathering Agent. Your job is to understand the complete user intent by asking clarifying questions until you have all necessary information.

Guidelines:
1. Ask specific questions to clarify ambiguous requests
2. Gather all required parameters for the task (locations for weather, expressions for calculations, queries for search)
3. Only mark intent as complete when you have sufficient details
4. Be conversational and helpful

When you have complete intent with all necessary details, respond with: "INTENT_COMPLETE: [detailed task description with all parameters]"

Examples:
- If user says "weather", ask for location
- If user says "calculate", ask for the specific calculation
- If user says "search", ask what they want to search for

Only use INTENT_COMPLETE when you have ALL the information needed to execute the task."""
    
    def process(self, state: AgentState) -> AgentState:
        messages = state["messages"]
        
        # Create conversation with system prompt
        conversation = [SystemMessage(content=self.system_prompt)]
        
        # Add conversation history (excluding system messages to avoid duplication)
        for msg in messages:
            if not isinstance(msg, SystemMessage):
                conversation.append(msg)
        
        # Get response from LLM
        response = self.llm.invoke(conversation, temperature=0.3)
        
        # Check if intent is complete
        if response.content.startswith("INTENT_COMPLETE:"):
            intent = response.content.replace("INTENT_COMPLETE:", "").strip()
            return {
                **state,
                "messages": [response],
                "user_intent": intent,
                "intent_complete": True,
                "task_instructions": intent,
                "next_agent": "executor"
            }
        else:
            return {
                **state,
                "messages": [response],
                "intent_complete": False,
                "next_agent": "intent_gatherer"
            }

# Agent 2: Task Execution Agent
class TaskExecutionAgent:
    def __init__(self, model="gemini-2.5-flash", api_key=None):
        self.llm = GeminiLLM(model=model, api_key=api_key)
        self.tools = {
            "get_weather": WeatherTool(),
            "calculator": CalculatorTool(),
            "search": SearchTool()
        }
        self.system_prompt = """You are a Task Execution Agent. You receive complete task instructions and must determine which tools to use and extract the necessary parameters.

Available tools:
- get_weather: Get weather information for a location (requires location parameter)
- calculator: Perform mathematical calculations (requires expression parameter)  
- search: Search for information (requires query parameter)

Analyze the task instructions and respond with a JSON object containing:
{
  "tool": "tool_name",
  "parameters": {
    "param_name": "param_value"
  },
  "reasoning": "why you chose this tool and these parameters"
}

Extract parameters carefully from the task instructions."""
    
    def process(self, state: AgentState) -> AgentState:
        task_instructions = state["task_instructions"]
        
        # Use LLM to determine tool and parameters
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Task: {task_instructions}")
        ]
        
        response = self.llm.invoke(messages, temperature=0.1)
        
        try:
            # Parse the LLM response to get tool and parameters
            tool_decision = json.loads(response.content)
            tool_name = tool_decision.get("tool")
            parameters = tool_decision.get("parameters", {})
            reasoning = tool_decision.get("reasoning", "")
            
            # Execute the tool
            tool_results = {}
            if tool_name in self.tools:
                if tool_name == "get_weather":
                    location = parameters.get("location", "unknown location")
                    result = self.tools[tool_name]._run(location)
                    tool_results["weather"] = result
                    
                elif tool_name == "calculator":
                    expression = parameters.get("expression", "0")
                    result = self.tools[tool_name]._run(expression)
                    tool_results["calculation"] = result
                    
                elif tool_name == "search":
                    query = parameters.get("query", "general search")
                    result = self.tools[tool_name]._run(query)
                    tool_results["search"] = result
            else:
                tool_results["error"] = f"Tool {tool_name} not found"
            
            # Create final response
            response_content = f"Task Analysis: {reasoning}\n\nResults: {json.dumps(tool_results, indent=2)}"
            
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            tool_results = {"error": "Could not parse tool selection", "raw_response": response.content}
            response_content = f"Error in tool selection. Raw response: {response.content}"
        
        final_response = AIMessage(content=response_content)
        
        return {
            **state,
            "messages": [final_response],
            "tool_results": tool_results,
            "next_agent": "end"
        }

# Multi-Agent System
class MultiAgentSystem:
    def __init__(self, model="gemini-2.5-flash", api_key=None):
        """
        Initialize the multi-agent system with Gemini
        
        Args:
            model: Gemini model name (default: "gemini-2.5-flash")
            api_key: Gemini API key (if None, uses GEMINI_API_KEY env var)
        """
        self.intent_agent = IntentGatheringAgent(model=model, api_key=api_key)
        self.executor_agent = TaskExecutionAgent(model=model, api_key=api_key)
        self.graph = self._build_graph()
    
    def _build_graph(self):
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("intent_gatherer", self._intent_gatherer_node)
        workflow.add_node("executor", self._executor_node)
        
        # Add edges
        workflow.set_entry_point("intent_gatherer")
        
        # Conditional routing
        workflow.add_conditional_edges(
            "intent_gatherer",
            self._route_after_intent,
            {
                "continue": "intent_gatherer",
                "execute": "executor"
            }
        )
        
        workflow.add_edge("executor", END)
        
        return workflow.compile()
    
    def _intent_gatherer_node(self, state: AgentState) -> AgentState:
        return self.intent_agent.process(state)
    
    def _executor_node(self, state: AgentState) -> AgentState:
        return self.executor_agent.process(state)
    
    def _route_after_intent(self, state: AgentState) -> str:
        if state.get("intent_complete", False):
            return "execute"
        else:
            return "continue"
    
    def run(self, user_input: str) -> str:
        """Run the multi-agent system with user input"""
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "user_intent": None,
            "intent_complete": False,
            "task_instructions": None,
            "tool_results": None,
            "next_agent": None
        }
        
        # Execute the graph
        final_state = self.graph.invoke(initial_state)
        
        # Return the last message
        return final_state["messages"][-1].content

# Configuration functions for Gemini
def create_gemini_system(model="gemini-2.5-flash"):
    """Standard Gemini configuration"""
    return MultiAgentSystem(model=model)

def create_gemini_system_with_key(model="gemini-2.5-flash", api_key=None):
    """Gemini configuration with explicit API key"""
    return MultiAgentSystem(model=model, api_key=api_key)

# Legacy functions for compatibility (now redirect to Gemini)
def create_openai_system(model="gemini-2.5-flash"):
    """Legacy function - now uses Gemini"""
    print("Note: Using Gemini 2.5 Flash instead of OpenAI")
    return MultiAgentSystem(model=model)

def create_azure_openai_system(deployment_name="gemini-2.5-flash", api_version=None):
    """Legacy function - now uses Gemini"""
    print("Note: Using Gemini 2.5 Flash instead of Azure OpenAI")
    return MultiAgentSystem(model=deployment_name)

def create_local_llm_system(base_url="gemini-2.5-flash"):
    """Legacy function - now uses Gemini"""
    print("Note: Using Gemini 2.5 Flash instead of local LLM")
    return MultiAgentSystem(model="gemini-2.5-flash")

# Example usage and testing
if __name__ == "__main__":
    # Initialize the multi-agent system with Gemini 2.5 Flash
    print("Initializing Multi-Agent System with Gemini 2.5 Flash...")
    
    # Standard Gemini configuration (uses GEMINI_API_KEY env var)
    system = create_gemini_system("gemini-2.5-flash")
    
    # Alternative configurations:
    # system = create_gemini_system_with_key("gemini-2.5-flash", "your-gemini-api-key")
    # system = MultiAgentSystem(model="gemini-2.5-flash", api_key="your-key")
    
    print("Multi-Agent System initialized with Gemini!")
    print("=" * 50)
    
    # Test scenarios
    test_cases = [
        "I want to know the weather",
        "Help me calculate something", 
        "I need to search for information"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: {test_input}")
        print("-" * 30)
        
        try:
            response = system.run(test_input)
            print(f"System Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
            print("Make sure you have set GEMINI_API_KEY environment variable")
        
        print("-" * 30)

# Interactive mode function
def interactive_mode():
    """Run the system in interactive mode with Gemini"""
    print("Multi-Agent System - Interactive Mode (Powered by Gemini 2.5 Flash)")
    print("Make sure you have set your GEMINI_API_KEY environment variable")
    print("Type 'quit' to exit")
    print("=" * 60)
    
    try:
        system = create_gemini_system("gemini-2.5-flash")
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
                
            if not user_input:
                continue
                
            try:
                response = system.run(user_input)
                print(f"System: {response}")
            except Exception as e:
                print(f"Error: {e}")
                print("Check your GEMINI_API_KEY and internet connection")
                
    except Exception as e:
        print(f"Failed to initialize system: {e}")
        print("Make sure you have set GEMINI_API_KEY environment variable")

# Uncomment to run interactive mode
# interactive_mode()