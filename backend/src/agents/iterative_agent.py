"""
Iterative Agent - An agent that can loop through tool calls and LLM reasoning
to complete complex tasks with controlled iteration count.
"""

import logging
import asyncio
from typing import Dict, Any, List, AsyncGenerator, Tuple, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from dataclasses import dataclass
import json

from src.llm.openai_compatible_llm import OpenAICompatibleLLM
from .tools.registry import tool_registry

logger = logging.getLogger(__name__)

@dataclass
class IterationStep:
    """Represents a single iteration step in the agent's reasoning process."""
    step_number: int
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    is_final: bool = False

class IterativeAgent:
    """
    An agent that can iteratively call tools and reason through problems
    with a controlled loop count to prevent excessive LLM calls.
    """
    
    def __init__(self, llm: OpenAICompatibleLLM, max_iterations: int = 5):
        self.llm = llm
        self.max_iterations = max_iterations
        self.tools = tool_registry.get_all_tools()
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        self.system_prompt = """You are an intelligent agent that can solve complex problems by breaking them down into steps and using available tools.

You work in iterations, following this pattern:
1. THOUGHT: Analyze the current situation and decide what to do next
2. ACTION: Choose a tool to use (if needed)
3. OBSERVATION: Receive the result from the tool
4. Repeat until you have enough information to provide a final answer

Available tools:
{tool_descriptions}

IMPORTANT INSTRUCTIONS:
- You have a maximum of {max_iterations} iterations to complete the task
- Each iteration should move you closer to solving the problem
- Use tools strategically - don't make unnecessary calls
- When you have enough information, provide a FINAL_ANSWER

Response format for each iteration:
THOUGHT: [Your reasoning about what to do next]
ACTION: [tool_name] 
ACTION_INPUT: [parameters for the tool as JSON]

OR if you're ready to answer:
THOUGHT: [Your final reasoning]
FINAL_ANSWER: [Your complete response to the user]

Examples:
THOUGHT: I need to get weather information for the user's location first.
ACTION: get_weather
ACTION_INPUT: {{"location": "New York"}}

THOUGHT: Now I have the weather data, I can provide a comprehensive answer.
FINAL_ANSWER: Based on the current weather in New York (72°F, sunny), it's a great day for outdoor activities.
"""
    
    def _get_tool_descriptions(self) -> str:
        """Get descriptions of available tools."""
        descriptions = []
        for tool in self.tools:
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)
    
    async def process_iteratively(
        self, 
        message: str, 
        conversation_history: List[BaseMessage] = None
    ) -> Tuple[str, List[IterationStep]]:
        """
        Process a message iteratively, returning the final answer and iteration history.
        
        Args:
            message: User message to process
            conversation_history: Previous conversation context
            
        Returns:
            Tuple of (final_answer, iteration_steps)
        """
        iteration_steps = []
        
        # Prepare initial messages
        messages = []
        
        # Add system message with tool descriptions
        system_content = self.system_prompt.format(
            tool_descriptions=self._get_tool_descriptions(),
            max_iterations=self.max_iterations
        )
        messages.append(SystemMessage(content=system_content))
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-5:])  # Keep last 5 messages for context
        
        # Add the user's current message
        messages.append(HumanMessage(content=message))
        
        # Start iterative processing
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"Starting iteration {iteration}/{self.max_iterations}")
            
            try:
                # Get LLM response (run blocking invoke in executor to avoid blocking event loop)
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, lambda: self.llm.invoke(messages))
                response_content = getattr(response, 'content', str(response))
                
                # Parse the response
                step = self._parse_iteration_response(response_content, iteration)
                iteration_steps.append(step)
                
                # Check if this is the final answer
                if step.is_final:
                    logger.info(f"Final answer reached in iteration {iteration}")
                    return step.observation or step.thought, iteration_steps
                
                # Execute the action if specified
                if step.action and step.action_input:
                    try:
                        observation = self._execute_tool(step.action, step.action_input)
                        step.observation = observation
                        
                        # Add the observation to the conversation
                        messages.append(AIMessage(content=response_content))
                        messages.append(HumanMessage(content=f"OBSERVATION: {observation}\n\nContinue with your next step."))
                        
                    except Exception as e:
                        error_msg = f"Error executing {step.action}: {str(e)}"
                        step.observation = error_msg
                        logger.error(error_msg)
                        
                        # Add error to conversation
                        messages.append(AIMessage(content=response_content))
                        messages.append(HumanMessage(content=f"OBSERVATION: {error_msg}\n\nTry a different approach."))
                
                else:
                    # No action specified, add the response and ask for next step
                    messages.append(AIMessage(content=response_content))
                    messages.append(HumanMessage(content="Continue with your next step or provide FINAL_ANSWER if ready."))
                
            except Exception as e:
                logger.error(f"Error in iteration {iteration}: {e}")
                error_step = IterationStep(
                    step_number=iteration,
                    thought=f"Error occurred: {str(e)}",
                    is_final=True
                )
                iteration_steps.append(error_step)
                return f"I encountered an error: {str(e)}", iteration_steps
        
        # If we've reached max iterations without a final answer
        logger.warning(f"Reached maximum iterations ({self.max_iterations}) without final answer")
        
        # Try to get a final answer based on what we've learned
        final_prompt = "Based on all the information gathered in the previous steps, please provide a FINAL_ANSWER to the user's question."
        messages.append(HumanMessage(content=final_prompt))
        
        try:
            # Ensure LLM invoke runs in executor
            loop = asyncio.get_event_loop()
            final_response = await loop.run_in_executor(None, lambda: self.llm.invoke(messages))
            final_step = IterationStep(
                step_number=self.max_iterations + 1,
                thought="Reached maximum iterations, providing final answer based on available information",
                observation=final_response.content,
                is_final=True
            )
            iteration_steps.append(final_step)
            return final_response.content, iteration_steps
        except Exception as e:
            logger.error(f"Error getting final response: {e}")
            return "I apologize, but I couldn't complete the task within the allowed iterations.", iteration_steps
    
    def _parse_iteration_response(self, response: str, iteration_number: int) -> IterationStep:
        """Parse the LLM response into an IterationStep."""
        import re
        
        step = IterationStep(step_number=iteration_number, thought="", is_final=False)
        
        # Check for FINAL_ANSWER
        final_answer_match = re.search(r'FINAL_ANSWER:\s*(.*)', response, re.DOTALL)
        if final_answer_match:
            step.is_final = True
            step.observation = final_answer_match.group(1).strip()
            
            # Also extract thought if present
            thought_match = re.search(r'THOUGHT:\s*(.*?)(?=FINAL_ANSWER|$)', response, re.DOTALL)
            if thought_match:
                step.thought = thought_match.group(1).strip()
            
            return step
        
        # Extract THOUGHT
        thought_match = re.search(r'THOUGHT:\s*(.*?)(?=ACTION|$)', response, re.DOTALL)
        if thought_match:
            step.thought = thought_match.group(1).strip()
        
        # Extract ACTION
        action_match = re.search(r'ACTION:\s*(\w+)', response)
        if action_match:
            step.action = action_match.group(1).strip()
        
        # Extract ACTION_INPUT
        action_input_match = re.search(r'ACTION_INPUT:\s*({.*?})', response, re.DOTALL)
        if action_input_match:
            try:
                step.action_input = json.loads(action_input_match.group(1))
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse ACTION_INPUT JSON: {e}")
                step.action_input = {"error": "Invalid JSON format"}
        
        return step
    
    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a tool with the given input."""
        if tool_name not in self.tool_map:
            return f"Error: Unknown tool '{tool_name}'. Available tools: {list(self.tool_map.keys())}"

        tool = self.tool_map[tool_name]

        try:
            # Always use the ToolAdapter's invoke method which handles LangChain tools properly
            result = tool.invoke(tool_input)
            return str(result)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error executing {tool_name}: {str(e)}"
    
    async def stream_process_iteratively(
        self, 
        message: str, 
        conversation_history: List[BaseMessage] = None
    ) -> AsyncGenerator[Tuple[str, bool, Optional[Dict]], None]:
        """
        Stream the iterative processing with a clean user experience.
        Shows minimal progress indicators and only the final answer.
        
        Yields:
            Tuple[str, bool, Optional[Dict]]: (content_chunk, is_complete, step_info)
        """
        try:
            logger.info(f"IterativeAgent: Starting to process message: '{message}'")
            
            iteration_steps = []
            
            # Prepare initial messages (same as process_iteratively)
            messages = []
            system_content = self.system_prompt.format(
                tool_descriptions=self._get_tool_descriptions(),
                max_iterations=self.max_iterations
            )
            messages.append(SystemMessage(content=system_content))
            
            if conversation_history:
                messages.extend(conversation_history[-5:])
            
            messages.append(HumanMessage(content=message))
            
            # Process iteratively with minimal user-facing updates
            for iteration in range(1, self.max_iterations + 1):
                logger.info(f"Processing iteration {iteration}/{self.max_iterations}")
                
                try:
                    response = self.llm.invoke(messages)
                    response_content = response.content
                    
                    step = self._parse_iteration_response(response_content, iteration)
                    iteration_steps.append(step)
                    
                    # Check if final answer
                    if step.is_final:
                        # Stream the final answer cleanly
                        final_answer = step.observation or step.thought
                        words = final_answer.split()
                        for word in words:
                            yield (word + " ", False, {"step": "final_answer"})
                            await asyncio.sleep(0.03)
                        
                        yield ("", True, {
                            "final": True, 
                            "total_iterations": iteration,
                            "steps": iteration_steps
                        })
                        return
                    
                    # Execute action if present (silently)
                    if step.action and step.action_input:
                        logger.info(f"Executing tool: {step.action}")
                        
                        try:
                            observation = self._execute_tool(step.action, step.action_input)
                            step.observation = observation
                            logger.info(f"Tool result: {observation[:100]}...")
                            
                            # Update conversation
                            messages.append(AIMessage(content=response_content))
                            messages.append(HumanMessage(content=f"OBSERVATION: {observation}\n\nContinue with your next step."))
                            
                        except Exception as e:
                            error_msg = f"Error executing {step.action}: {str(e)}"
                            step.observation = error_msg
                            logger.error(error_msg)
                            
                            messages.append(AIMessage(content=response_content))
                            messages.append(HumanMessage(content=f"OBSERVATION: {error_msg}\n\nTry a different approach."))
                    else:
                        messages.append(AIMessage(content=response_content))
                        messages.append(HumanMessage(content="Continue with your next step or provide FINAL_ANSWER if ready."))
                    
                except Exception as e:
                    logger.error(f"Error in iteration {iteration}: {e}")
                    error_response = f"I apologize, but I encountered an error while processing your request: {str(e)}"
                    words = error_response.split()
                    for word in words:
                        yield (word + " ", False, {"step": "error"})
                        await asyncio.sleep(0.03)
                    yield ("", True, {"error": True, "steps": iteration_steps})
                    return
            
            # Max iterations reached - try to get final answer
            logger.warning(f"Reached maximum iterations ({self.max_iterations})")
            
            final_prompt = "Based on all the information gathered, please provide a FINAL_ANSWER."
            messages.append(HumanMessage(content=final_prompt))
            
            try:
                final_response = self.llm.invoke(messages)
                words = final_response.content.split()
                for word in words:
                    yield (word + " ", False, {"step": "final_answer"})
                    await asyncio.sleep(0.03)
                
                yield ("", True, {
                    "final": True,
                    "max_iterations_reached": True,
                    "total_iterations": self.max_iterations,
                    "steps": iteration_steps
                })
            except Exception as e:
                logger.error(f"Could not generate final answer: {e}")
                error_response = "I apologize, but I couldn't complete your request within the available processing time."
                words = error_response.split()
                for word in words:
                    yield (word + " ", False, {"step": "error"})
                    await asyncio.sleep(0.03)
                yield ("", True, {"error": True, "steps": iteration_steps})
                
        except Exception as e:
            logger.error(f"Error in stream_process_iteratively: {e}")
            error_response = f"I apologize, but I encountered a fatal error: {str(e)}"
            words = error_response.split()
            for word in words:
                yield (word + " ", False, {"step": "error"})
                await asyncio.sleep(0.03)
            yield ("", True, {"error": True})