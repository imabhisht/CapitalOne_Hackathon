"""
LangGraph agent implementation with tool calling capabilities.
"""

import logging
import re
import asyncio
from typing import Dict, Any, List, AsyncGenerator, Tuple, Annotated
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from src.llm.openai_compatible_llm import OpenAICompatibleLLM
from .tools.registry import tool_registry

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State for the LangGraph agent."""
    messages: Annotated[List[BaseMessage], add_messages]
    tool_calls_made: bool
    
class LangGraphAgent:
    """
    LangGraph agent with tool calling capabilities using proper LangGraph patterns.
    """
    
    def __init__(self, llm: OpenAICompatibleLLM):
        self.llm = llm
        self.tools = tool_registry.get_all_tools()
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        # Build the graph
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        """
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", self._call_tools)
        
        # Set entry point
        workflow.add_edge(START, "agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "tools": "tools",
                "end": END,
            },
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def _call_model(self, state: AgentState) -> AgentState:
        """
        Call the LLM with the current state.
        """
        try:
            messages = state["messages"]
            logger.info(f"_call_model received {len(messages)} messages")
            
            # Enhance system message with tool information if not already done
            enhanced_messages = self._ensure_tool_instructions(messages)
            
            logger.info(f"Sending {len(enhanced_messages)} enhanced messages to LLM")
            response = self.llm.invoke(enhanced_messages)
            
            return {
                "messages": [response],
                "tool_calls_made": False
            }
        except Exception as e:
            logger.error(f"Error calling model: {e}")
            error_msg = AIMessage(content=f"I encountered an error: {str(e)}")
            return {
                "messages": [error_msg],
                "tool_calls_made": False
            }
    
    def _ensure_tool_instructions(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """Ensure the system message includes tool instructions."""
        if not messages:
            return messages
            
        enhanced_messages = []
        tool_descriptions = self._get_tool_descriptions()
        
        for i, msg in enumerate(messages):
            if isinstance(msg, SystemMessage) and i == 0:
                # Check if tool instructions are already present
                if "TOOL_CALL:" not in msg.content:
                    enhanced_content = f"""{msg.content}

Available tools:
{tool_descriptions}

When you need to use a tool, respond with: TOOL_CALL: tool_name(parameters)
Examples:
- TOOL_CALL: get_location() - to get location information
- TOOL_CALL: get_weather("Baroda, Jamjodhpur") - to get weather
- TOOL_CALL: calculate("25 * 4 + 10") - to perform calculations

After using a tool, I'll provide you with the results and you should give a natural response based on those results.
"""
                    enhanced_messages.append(SystemMessage(content=enhanced_content))
                else:
                    enhanced_messages.append(msg)
            else:
                enhanced_messages.append(msg)
        
        return enhanced_messages
    
    def _get_tool_descriptions(self) -> str:
        """Get descriptions of available tools."""
        descriptions = []
        for tool in self.tools:
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)
    
    def _should_continue(self, state: AgentState) -> str:
        """
        Determine whether to continue with tool calls or end.
        """
        messages = state["messages"]
        if not messages:
            return "end"
            
        last_message = messages[-1]
        
        # Check if the response contains a tool call and we haven't made tool calls yet
        if (isinstance(last_message, AIMessage) and 
            "TOOL_CALL:" in last_message.content and 
            not state.get("tool_calls_made", False)):
            return "tools"
        
        return "end"
    
    def _call_tools(self, state: AgentState) -> AgentState:
        """
        Execute tool calls from the last message.
        """
        messages = state["messages"]
        if not messages:
            return {"messages": [], "tool_calls_made": True}
            
        last_message = messages[-1]
        
        if not isinstance(last_message, AIMessage):
            return {"messages": [], "tool_calls_made": True}
        
        # Extract tool calls from the message
        tool_calls = self._extract_tool_calls(last_message.content)
        
        if not tool_calls:
            return {"messages": [], "tool_calls_made": True}
        
        tool_results = []
        for tool_call in tool_calls:
            try:
                result = self._execute_tool_call(tool_call)
                tool_results.append(f"Tool '{tool_call['name']}' result: {result}")
            except Exception as e:
                logger.error(f"Error executing tool {tool_call['name']}: {e}")
                tool_results.append(f"Tool '{tool_call['name']}' error: {str(e)}")
        
        # Create a message with tool results
        tool_message = HumanMessage(
            content=f"Tool results:\n" + "\n".join(tool_results) + 
                   "\n\nPlease provide a natural response based on these results."
        )
        
        return {
            "messages": [tool_message],
            "tool_calls_made": True
        }
    
    def _extract_tool_calls(self, content: str) -> List[Dict]:
        """Extract tool calls from message content."""
        tool_calls = []
        
        # Look for TOOL_CALL: pattern
        pattern = r'TOOL_CALL:\s*(\w+)\((.*?)\)'
        matches = re.findall(pattern, content)
        
        for match in matches:
            tool_name, params = match
            
            # Parse parameters
            parsed_params = {}
            if params.strip():
                # Remove quotes if present
                param_value = params.strip().strip('"').strip("'")
                
                # Map to appropriate parameter name based on tool
                if tool_name == "calculate":
                    parsed_params = {"expression": param_value}
                elif tool_name == "get_weather":
                    parsed_params = {"location": param_value}
                else:
                    parsed_params = {"query": param_value}
            
            tool_calls.append({
                "name": tool_name,
                "parameters": parsed_params
            })
        
        return tool_calls
    
    def _execute_tool_call(self, tool_call: Dict) -> Any:
        """Execute a single tool call."""
        tool_name = tool_call["name"]
        parameters = tool_call["parameters"]
        
        if tool_name not in self.tool_map:
            return f"Error: Unknown tool '{tool_name}'"
        
        tool = self.tool_map[tool_name]
        
        try:
            # Execute the tool with parameters
            if parameters:
                # Get the first parameter value for single-parameter tools
                param_value = list(parameters.values())[0] if parameters else ""
                result = tool.invoke(param_value)
            else:
                result = tool.invoke("")
            
            return result
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error executing {tool_name}: {str(e)}"
    
    async def invoke(self, message: str, conversation_history: List = None) -> str:
        """
        Invoke the agent with a message.
        
        Args:
            message: User message
            conversation_history: Previous conversation messages
            
        Returns:
            Agent response
        """
        try:
            # Prepare messages
            messages = []
            
            # Add system message
            system_msg = SystemMessage(content="""You are a helpful AI assistant. You have access to several tools that can help you provide better responses.""")
            messages.append(system_msg)
            
            # Add conversation history if provided
            if conversation_history:
                logger.info(f"Adding {len(conversation_history)} messages from conversation history")
                messages.extend(conversation_history[-10:])  # Keep last 10 messages
            else:
                logger.info("No conversation history provided")
            
            # Add current user message
            messages.append(HumanMessage(content=message))
            
            logger.info(f"Total messages being sent to graph: {len(messages)}")
            
            # Create initial state
            initial_state = {
                "messages": messages,
                "tool_calls_made": False
            }
            
            # Run the graph
            result = await self.graph.ainvoke(initial_state)
            
            # Get the final response - look for the last AI message
            final_messages = result["messages"]
            
            # Find the last AI message that's not a tool call
            for msg in reversed(final_messages):
                if isinstance(msg, AIMessage) and not "TOOL_CALL:" in msg.content:
                    return msg.content
            
            # Fallback to last message
            if final_messages:
                last_message = final_messages[-1]
                if hasattr(last_message, 'content'):
                    return last_message.content
                else:
                    return str(last_message)
            
            return "I apologize, but I couldn't generate a response."
                
        except Exception as e:
            logger.error(f"Error in agent invoke: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    async def stream_invoke(self, message: str, conversation_history: List = None) -> AsyncGenerator[Tuple[str, bool], None]:
        """
        Stream the agent response.
        
        Args:
            message: User message
            conversation_history: Previous conversation messages
            
        Yields:
            Tuple[str, bool]: (content_chunk, is_complete)
        """
        try:
            # Get the full response first
            response = await self.invoke(message, conversation_history)
            
            # Stream it word by word
            words = response.split()
            for word in words:
                yield (word + " ", False)
                # Small delay to simulate streaming
                await asyncio.sleep(0.03)
            
            yield ("", True)  # Signal completion
            
        except Exception as e:
            logger.error(f"Error in agent stream_invoke: {e}")
            error_message = f"I apologize, but I encountered an error: {str(e)}"
            words = error_message.split()
            for word in words:
                yield (word + " ", False)
                await asyncio.sleep(0.03)
            yield ("", True)