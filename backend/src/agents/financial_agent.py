"""
Financial Agent - Specialized in financial advice, calculations, and planning.
"""

from typing import List
from .base_agent import BaseAgent
from .tools.registry import tool_registry

class FinancialAgent(BaseAgent):
    """Agent specialized in financial advice and calculations."""
    
    def __init__(self, llm):
        system_prompt = """You are a knowledgeable Financial Advisor with expertise in personal and business finance.

Your expertise includes:
- Financial planning and budgeting
- Investment strategies and portfolio management
- Loan calculations and mortgage planning
- Tax planning and optimization
- Retirement planning
- Insurance planning
- Business financial analysis
- Agricultural finance and farm economics
- Risk management
- Financial calculations (ROI, NPV, compound interest, etc.)
- Market analysis and trends
- Debt management strategies

Available tools:
- calculate: For mathematical calculations (use format: TOOL_CALL: calculate("expression"))

When users need financial calculations, use the calculator tool. For complex financial advice, provide detailed explanations with practical examples.

Always remind users that this is general financial information and they should consult with qualified financial professionals for personalized advice."""
        
        super().__init__("Financial Advisor", llm, system_prompt)
        self.tools = tool_registry.get_all_tools()
        self.tool_map = {tool.name: tool for tool in self.tools}
    
    def can_handle(self, query: str) -> bool:
        """Check if this agent can handle the financial query."""
        financial_keywords = self.get_keywords()
        query_lower = query.lower()
        
        return any(keyword in query_lower for keyword in financial_keywords)
    
    def get_keywords(self) -> List[str]:
        """Return keywords related to finance."""
        return [
            "finance", "financial", "money", "budget", "investment", "loan",
            "mortgage", "interest", "tax", "retirement", "insurance", "savings",
            "profit", "loss", "revenue", "cost", "calculate", "calculation",
            "roi", "return", "portfolio", "stock", "bond", "mutual fund",
            "bank", "credit", "debt", "income", "expense", "cash flow",
            "compound", "simple interest", "npv", "irr", "payback period",
            "financial planning", "wealth", "asset", "liability", "equity"
        ]
    
    async def process(self, message: str, conversation_history=None) -> str:
        """Process financial queries with tool support."""
        # Check if this might need calculation
        if any(word in message.lower() for word in ["calculate", "compute", "math", "+", "-", "*", "/", "%"]):
            # Let the LLM decide if it needs to use tools
            response = await super().process(message, conversation_history)
            
            # Check if response contains tool calls
            if "TOOL_CALL:" in response:
                return await self._handle_tool_calls(response, message, conversation_history)
            
            return response
        else:
            return await super().process(message, conversation_history)
    
    async def _handle_tool_calls(self, response: str, original_message: str, conversation_history=None) -> str:
        """Handle tool calls in the response."""
        import re
        
        # Extract tool calls
        pattern = r'TOOL_CALL:\s*(\w+)\((.*?)\)'
        matches = re.findall(pattern, response)
        
        tool_results = []
        for match in matches:
            tool_name, params = match
            if tool_name in self.tool_map:
                try:
                    # Remove quotes from params
                    param_value = params.strip().strip('"').strip("'")
                    result = self.tool_map[tool_name].invoke(param_value)
                    tool_results.append(f"Calculation result: {result}")
                except Exception as e:
                    tool_results.append(f"Calculation error: {str(e)}")
        
        if tool_results:
            # Get a natural response based on tool results
            follow_up_message = f"Based on the calculation results: {'; '.join(tool_results)}, please provide a comprehensive financial analysis and advice for the original question: {original_message}"
            return await super().process(follow_up_message, conversation_history)
        
        return response