"""
Agent Coordinator - Routes queries to appropriate specialized agents and can use multiple agents in parallel.
Enhanced with iterative processing capabilities.
"""

import logging
import asyncio
from typing import List, Dict, Any, AsyncGenerator, Tuple, Optional
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

from src.llm.openai_compatible_llm import OpenAICompatibleLLM
from .organic_farming_agent import OrganicFarmingAgent
from .financial_agent import FinancialAgent
from .weather_agent import WeatherAgent
from .general_chat_agent import GeneralChatAgent
from .iterative_agent import IterativeAgent

logger = logging.getLogger(__name__)

class AgentCoordinator:
    """
    Coordinates multiple specialized agents and routes queries appropriately.
    Can use multiple agents in parallel for complex queries.
    """

    def __init__(self, llm: OpenAICompatibleLLM, small_llm: OpenAICompatibleLLM):
        self.llm = llm
        self.small_llm = small_llm
        
        # Initialize specialized agents
        self.agents = {
            "organic_farming": OrganicFarmingAgent(llm),
            "financial": FinancialAgent(llm),
            "weather": WeatherAgent(llm),
            "general": GeneralChatAgent(llm)
        }
        
        # Initialize iterative agent for complex tasks
        self.iterative_agent = IterativeAgent(llm, max_iterations=5)
        
        # Routing system prompt
        self.routing_prompt = """You are an intelligent query router that determines how to handle a user query.

Available processing modes:
1. SIMPLE - Use specialized agents for straightforward queries
2. ITERATIVE - Use iterative processing for complex multi-step tasks that require tool usage and reasoning

Available agents (for SIMPLE mode):
1. organic_farming - Handles organic farming, agriculture, crops, soil, pest management, sustainable farming
2. financial - Handles financial advice, calculations, budgeting, investments, loans, agricultural economics
3. weather - Handles weather information, forecasts, agricultural weather planning
4. general - Handles general conversations and queries not covered by other agents

Use ITERATIVE mode for queries that:
- Require multiple steps or tools to complete
- Need data gathering and analysis
- Involve complex problem-solving
- Require calculations with external data
- Need to combine information from multiple sources
- Ask about weather without specifying location (need to get location first)
- Require real-time data or current information

Use SIMPLE mode for:
- Direct questions with straightforward answers
- General conversations
- Single-domain expertise queries
- Weather queries with specific location already provided

Respond in this format:
MODE: [SIMPLE/ITERATIVE]
AGENTS: [agent_name1, agent_name2, ...] (only for SIMPLE mode)
PARALLEL: [yes/no] - whether agents should work in parallel (only for SIMPLE mode)
REASONING: Brief explanation of your routing decision

Examples:
- "What's the weather today?" -> MODE: ITERATIVE (needs location detection and weather data)
- "What's the weather in New York?" -> MODE: SIMPLE, AGENTS: [weather], PARALLEL: no
- "Calculate the ROI for a 10-acre organic farm with current market prices" -> MODE: ITERATIVE
- "Hello, how are you?" -> MODE: SIMPLE, AGENTS: [general], PARALLEL: no
- "Help me plan a complete farming strategy including weather, costs, and crop selection" -> MODE: ITERATIVE"""
    
    async def route_query(self, query: str) -> Dict[str, Any]:
        """Route a query to determine which agents should handle it."""
        try:
            messages = [
                SystemMessage(content=self.routing_prompt),
                HumanMessage(content=f"Route this query: {query}")
            ]

            response = self.small_llm.invoke(messages)
            routing_decision = self._parse_routing_response(response.content)
            logger.info(f"LLM routing response: {response.content}")
            logger.info(f"Parsed routing decision: {routing_decision}")
            
            # Fallback routing if parsing fails
            if not routing_decision.get("mode") and not routing_decision.get("agents"):
                logger.info("Using fallback routing due to parsing failure")
                routing_decision = self._fallback_routing(query)
            
            return routing_decision
            
        except Exception as e:
            logger.error(f"Error in query routing: {e}")
            return self._fallback_routing(query)
    
    def _parse_routing_response(self, response: str) -> Dict[str, Any]:
        """Parse the routing response from the LLM."""
        import re
        
        mode = "SIMPLE"  # default
        agents = []
        parallel = False
        reasoning = ""
        
        # Extract mode
        mode_match = re.search(r'MODE:\s*(SIMPLE|ITERATIVE)', response, re.IGNORECASE)
        if mode_match:
            mode = mode_match.group(1).upper()
        
        # Extract agents (only relevant for SIMPLE mode)
        agents_match = re.search(r'AGENTS:\s*\[(.*?)\]', response)
        if agents_match:
            agents_str = agents_match.group(1)
            agents = [agent.strip().strip('"').strip("'") for agent in agents_str.split(",") if agent.strip()]
        
        # Extract parallel flag
        parallel_match = re.search(r'PARALLEL:\s*(yes|no)', response, re.IGNORECASE)
        if parallel_match:
            parallel = parallel_match.group(1).lower() == "yes"
        
        # Extract reasoning
        reasoning_match = re.search(r'REASONING:\s*(.*)', response, re.DOTALL)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        
        return {
            "mode": mode,
            "agents": agents,
            "parallel": parallel,
            "reasoning": reasoning
        }
    
    def _fallback_routing(self, query: str) -> Dict[str, Any]:
        """Fallback routing based on keyword matching."""
        query_lower = query.lower()
        
        # Check for complex task indicators
        complex_indicators = [
            "calculate", "analyze", "plan", "compare", "research", 
            "find out", "determine", "evaluate", "optimize", "strategy"
        ]
        
        # Check for weather queries without specific location
        weather_without_location = (
            "weather" in query_lower and 
            not any(location in query_lower for location in [
                "in ", "at ", "for ", "new york", "london", "paris", "tokyo", 
                "mumbai", "delhi", "bangalore", "chennai", "kolkata", "hyderabad",
                "baroda", "vadodara", "ahmedabad", "surat", "rajkot"
            ])
        )
        
        is_complex = any(indicator in query_lower for indicator in complex_indicators) or weather_without_location
        
        if is_complex:
            logger.info(f"Fallback routing: Query '{query}' classified as complex (weather_without_location: {weather_without_location})")
            return {
                "mode": "ITERATIVE",
                "agents": [],
                "parallel": False,
                "reasoning": f"Fallback routing detected complex task requiring iterative processing. Weather without location: {weather_without_location}"
            }
        
        # Check each agent's keywords for simple routing
        matching_agents = []
        for agent_name, agent in self.agents.items():
            if agent_name != "general" and agent.can_handle(query):
                matching_agents.append(agent_name)
        
        # If no specialized agents match, use general
        if not matching_agents:
            matching_agents = ["general"]
        
        # Determine if parallel processing is beneficial
        parallel = len(matching_agents) > 1
        
        return {
            "mode": "SIMPLE",
            "agents": matching_agents,
            "parallel": parallel,
            "reasoning": f"Fallback routing based on keyword matching. Found {len(matching_agents)} matching agents."
        }
    
    async def process_query(self, query: str, conversation_history: List[BaseMessage] = None) -> str:
        """Process a query using the appropriate agent(s) or iterative processing."""
        try:
            # Route the query
            routing = await self.route_query(query)
            mode = routing.get("mode", "SIMPLE")
            agent_names = routing.get("agents", [])
            use_parallel = routing.get("parallel", False)
            
            logger.info(f"Routing query - Mode: {mode}, Agents: {agent_names}, Parallel: {use_parallel}")
            
            # Use iterative processing for complex tasks
            if mode == "ITERATIVE":
                logger.info("Using iterative agent for complex task processing")
                final_answer, iteration_steps = await self.iterative_agent.process_iteratively(
                    query, conversation_history
                )
                return final_answer
            
            # Use simple agent routing for straightforward queries
            if not agent_names:
                return "I apologize, but I couldn't determine how to handle your query."
            
            # Process with single agent
            if len(agent_names) == 1:
                agent_name = agent_names[0]
                if agent_name in self.agents:
                    return await self.agents[agent_name].process(query, conversation_history)
                else:
                    return await self.agents["general"].process(query, conversation_history)
            
            # Process with multiple agents
            if use_parallel:
                return await self._process_parallel(agent_names, query, conversation_history)
            else:
                return await self._process_sequential(agent_names, query, conversation_history)
                
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return f"I apologize, but I encountered an error while processing your query: {str(e)}"
    
    async def _process_parallel(self, agent_names: List[str], query: str, conversation_history: List[BaseMessage] = None) -> str:
        """Process query with multiple agents in parallel."""
        tasks = []
        valid_agents = []
        
        for agent_name in agent_names:
            if agent_name in self.agents:
                tasks.append(self.agents[agent_name].process(query, conversation_history))
                valid_agents.append(agent_name)
        
        if not tasks:
            return await self.agents["general"].process(query, conversation_history)
        
        # Run agents in parallel
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine responses
        combined_response = "Here's what I found from multiple perspectives:\n\n"
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.error(f"Error from {valid_agents[i]} agent: {response}")
                continue
                
            agent_name = valid_agents[i].replace("_", " ").title()
            combined_response += f"**{agent_name} Perspective:**\n{response}\n\n"
        
        return combined_response.strip()
    
    async def _process_sequential(self, agent_names: List[str], query: str, conversation_history: List[BaseMessage] = None) -> str:
        """Process query with multiple agents sequentially."""
        responses = []
        
        for agent_name in agent_names:
            if agent_name in self.agents:
                try:
                    response = await self.agents[agent_name].process(query, conversation_history)
                    responses.append((agent_name, response))
                except Exception as e:
                    logger.error(f"Error from {agent_name} agent: {e}")
        
        if not responses:
            return await self.agents["general"].process(query, conversation_history)
        
        # If only one response, return it directly
        if len(responses) == 1:
            return responses[0][1]
        
        # Combine multiple responses
        combined_response = "Here's a comprehensive response:\n\n"
        for agent_name, response in responses:
            agent_display_name = agent_name.replace("_", " ").title()
            combined_response += f"**{agent_display_name}:**\n{response}\n\n"
        
        return combined_response.strip()
    
    async def stream_process_query(self, query: str, conversation_history: List[BaseMessage] = None) -> AsyncGenerator[Tuple[str, bool], None]:
        """Stream the response for a query with enhanced iterative processing."""
        try:
            # Route the query first
            routing = await self.route_query(query)
            mode = routing.get("mode", "SIMPLE")
            agent_names = routing.get("agents", [])
            use_parallel = routing.get("parallel", False)
            
            logger.info(f"Streaming query - Mode: {mode}, Agents: {agent_names}, Parallel: {use_parallel}")
            
            # Use iterative streaming for complex tasks
            if mode == "ITERATIVE":
                logger.info("Using iterative streaming for complex task")
                async for chunk, is_complete, step_info in self.iterative_agent.stream_process_iteratively(
                    query, conversation_history
                ):
                    yield (chunk, is_complete)
                return
            
            # Use regular streaming for simple tasks
            response = await self.process_query(query, conversation_history)
            
            # Stream it word by word
            words = response.split()
            for word in words:
                yield (word + " ", False)
                await asyncio.sleep(0.03)
            
            yield ("", True)  # Signal completion
            
        except Exception as e:
            logger.error(f"Error in stream_process_query: {e}")
            error_message = f"I apologize, but I encountered an error: {str(e)}"
            words = error_message.split()
            for word in words:
                yield (word + " ", False)
                await asyncio.sleep(0.03)
            yield ("", True)
    
    def get_agent_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all available agents."""
        agent_info = {}
        for name, agent in self.agents.items():
            agent_info[name] = {
                "name": agent.name,
                "keywords": agent.get_keywords(),
                "description": f"Specialized in {name.replace('_', ' ')}"
            }
        return agent_info