from src.llm.openai_compatible_llm import OpenAICompatibleLLM
from src.models.agent_state import AgentState
from langchain_core.messages import SystemMessage

class IntentGatheringAgent:
    def __init__(self, model="gemini-2.5-flash", api_key=None):
        self.llm = OpenAICompatibleLLM(model=model, api_key=api_key)
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