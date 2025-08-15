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

# Generic LLM wrapper using OpenAI SDK specification
class OpenAICompatibleLLM:
    def __init__(self, model=None, api_key=None, base_url=None):
        """
        Initialize LLM client using OpenAI SDK format
        
        Args:
            model: LLM model name (e.g., "gpt-4", "gemini-2.5-flash", "claude-3-sonnet")
            api_key: LLM API key (if None, will use LLM_API_KEY env var)
            base_url: API base URL (if None, will use LLM_BASE_URL env var)
        """
        self.model = model or os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.client = OpenAI(
            api_key=api_key or os.getenv("LLM_API_KEY"),
            base_url=base_url or os.getenv("LLM_BASE_URL")
        )
    
    def invoke(self, messages, temperature=0.7, max_tokens=1000):
        """
        Invoke LLM with messages using OpenAI specification
        
        Args:
            messages: List of BaseMessage objects
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
        """
        # Convert LangChain messages to OpenAI format
        openai_messages = []
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                openai_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                openai_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                openai_messages.append({"role": "assistant", "content": msg.content})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            return AIMessage(content=content)
            
        except Exception as e:
            return AIMessage(content=f"Error calling LLM: {str(e)}")

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
    def __init__(self, model=None, api_key=None, base_url=None):
        self.llm = OpenAICompatibleLLM(model=model, api_key=api_key, base_url=base_url)
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
    def __init__(self, model=None, api_key=None, base_url=None):
        self.llm = OpenAICompatibleLLM(model=model, api_key=api_key, base_url=base_url)
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
    def __init__(self, model=None, api_key=None, base_url=None):
        """
        Initialize the multi-agent system with OpenAI-compatible LLM
        
        Args:
            model: LLM model name (default: from LLM_MODEL env var or "gpt-3.5-turbo")
            api_key: LLM API key (if None, uses LLM_API_KEY env var)
            base_url: API base URL (if None, uses LLM_BASE_URL env var)
        """
        self.intent_agent = IntentGatheringAgent(model=model, api_key=api_key, base_url=base_url)
        self.executor_agent = TaskExecutionAgent(model=model, api_key=api_key, base_url=base_url)
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

# Configuration functions for OpenAI-compatible LLMs
def create_llm_system(model=None, api_key=None, base_url=None):
    """Standard LLM configuration using environment variables"""
    return MultiAgentSystem(model=model, api_key=api_key, base_url=base_url)

def create_openai_system(model="gpt-3.5-turbo", api_key=None):
    """OpenAI configuration"""
    return MultiAgentSystem(model=model, api_key=api_key)

def create_openrouter_system(model="openai/gpt-3.5-turbo", api_key=None):
    """OpenRouter configuration"""
    return MultiAgentSystem(
        model=model, 
        api_key=api_key, 
        base_url="https://openrouter.ai/api/v1"
    )

def create_gemini_system(model="gemini-2.5-flash", api_key=None):
    """Gemini configuration via OpenRouter or direct API"""
    return MultiAgentSystem(
        model=model, 
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

def create_claude_system(model="anthropic/claude-3-sonnet", api_key=None):
    """Claude configuration via OpenRouter"""
    return MultiAgentSystem(
        model=model, 
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

def create_local_llm_system(model="llama2", base_url="http://localhost:11434/v1"):
    """Local LLM configuration (e.g., Ollama)"""
    return MultiAgentSystem(model=model, base_url=base_url)

# Example usage and testing
if __name__ == "__main__":
    # Initialize the multi-agent system with environment configuration
    print("Initializing Multi-Agent System with OpenAI-compatible LLM...")
    
    # Standard configuration (uses LLM_MODEL, LLM_API_KEY, LLM_BASE_URL env vars)
    system = create_llm_system()
    
    # Alternative configurations:
    # system = create_openai_system("gpt-4", "your-openai-api-key")
    # system = create_gemini_system("gemini-2.5-flash", "your-gemini-api-key")
    # system = create_openrouter_system("anthropic/claude-3-sonnet", "your-openrouter-key")
    # system = create_local_llm_system("llama2", "http://localhost:11434/v1")
    
    print("Multi-Agent System initialized!")
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
            print("Make sure you have set LLM_API_KEY and LLM_BASE_URL environment variables")
        
        print("-" * 30)

# Interactive mode function
def interactive_mode():
    """Run the system in interactive mode with OpenAI-compatible LLM"""
    print("Multi-Agent System - Interactive Mode")
    print("Make sure you have set your LLM_API_KEY and LLM_BASE_URL environment variables")
    print("Type 'quit' to exit")
    print("=" * 60)
    
    try:
        system = create_llm_system()
        
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
                print("Check your LLM_API_KEY, LLM_BASE_URL and internet connection")
                
    except Exception as e:
        print(f"Failed to initialize system: {e}")
        print("Make sure you have set LLM_API_KEY and LLM_BASE_URL environment variables")

# Uncomment to run interactive mode
# interactive_mode()