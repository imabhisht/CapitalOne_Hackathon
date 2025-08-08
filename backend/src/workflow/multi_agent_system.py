

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