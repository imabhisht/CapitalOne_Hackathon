import operator
from typing import Annotated, Dict, List, Optional, TypedDict
from langchain_core.messages import BaseMessage

# State definition for the multi-agent system
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_intent: Optional[str]
    intent_complete: bool
    task_instructions: Optional[str]
    tool_results: Optional[Dict]
    next_agent: Optional[str]
