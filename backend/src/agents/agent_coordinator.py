"""
Agent Coordinator - Routes queries to appropriate specialized agents and can use multiple agents in parallel.
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

logger = logging.getLogger(__name__)

class AgentCoordinator:
    """
    Coordinates multiple specialized agents and routes queries appropriately.
    Can use multiple agents in parallel for complex queries.
    """
    
    def __init__(self, llm: OpenAICompatibleLLM):
        self.llm = llm
        
        # Initialize specialized agents
        self.agents = {
            "organic_farming": OrganicFarmingAgent(llm),
            "financial": FinancialAgent(llm),
            "weather": WeatherAgent(llm),
            "general": GeneralChatAgent(llm)
        }
        
        # Routing system prompt
        self.routing_prompt = """You are an intelligent query router that determines which specialized agents should handle a user query.

Available agents:
1. organic_farming - Handles organic farming, agriculture, crops, soil, pest management, sustainable farming
2. financial - Handles financial advice, calculations, budgeting, investments, loans, agricultural economics
3. weather - Handles weather information, forecasts, agricultural weather planning
4. general - Handles general conversations and queries not covered by other agents

Analyze the user query and determine:
1. Which agent(s) should handle this query
2. Whether multiple agents should work together (for complex queries)
3. The priority order if multiple agents are needed

Respond in this format:
AGENTS: [agent_name1, agent_name2, ...]
PARALLEL: [yes/no] - whether agents should work in parallel
REASONING: Brief explanation of your routing decision

Examples:
- "What's the weather for farming?" -> AGENTS: [weather], PARALLEL: no
- "How much profit can I make from organic tomatoes?" -> AGENTS: [organic_farming, financial], PARALLEL: yes
- "Hello, how are you?" -> AGENTS: [general], PARALLEL: no"""
    
    async def route_query(self, query: str) -> Dict[str, Any]:
        """Route a query to determine which agents should handle it."""
        try:
            messages = [
                SystemMessage(content=self.routing_prompt),
                HumanMessage(content=f"Route this query: {query}")
            ]
            
            response = self.llm.invoke(messages)
            routing_decision = self._parse_routing_response(response.content)
            
            # Fallback routing if parsing fails
            if not routing_decision["agents"]:
                routing_decision = self._fallback_routing(query)
            
            return routing_decision
            
        except Exception as e:
            logger.error(f"Error in query routing: {e}")
            return self._fallback_routing(query)
    
    def _parse_routing_response(self, response: str) -> Dict[str, Any]:
        """Parse the routing response from the LLM."""
        import re
        
        agents = []
        parallel = False
        reasoning = ""
        
        # Extract agents
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
            "agents": agents,
            "parallel": parallel,
            "reasoning": reasoning
        }
    
    def _fallback_routing(self, query: str) -> Dict[str, Any]:
        """Fallback routing based on keyword matching."""
        query_lower = query.lower()
        
        # Check each agent's keywords
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
            "agents": matching_agents,
            "parallel": parallel,
            "reasoning": f"Fallback routing based on keyword matching. Found {len(matching_agents)} matching agents."
        }
    
    async def process_query(self, query: str, conversation_history: List[BaseMessage] = None) -> str:
        """Process a query using the appropriate agent(s)."""
        try:
            # Route the query
            routing = await self.route_query(query)
            agent_names = routing["agents"]
            use_parallel = routing["parallel"]
            
            logger.info(f"Routing query to agents: {agent_names}, parallel: {use_parallel}")
            
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
        """Stream the response for a query."""
        try:
            # Get the full response first
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