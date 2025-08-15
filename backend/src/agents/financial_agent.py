"""
Financial Agent - Specialized in financial advice, calculations, and planning.
"""

import logging
from typing import List
from .base_agent import BaseAgent
from .tools.registry import tool_registry

logger = logging.getLogger(__name__)

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

IMPORTANT: You have access to a calculation tool that you MUST use for any mathematical operations:

TOOL USAGE INSTRUCTIONS:
For ANY mathematical calculation, you MUST use the calculator tool with this EXACT format:
TOOL_CALL: calculate("mathematical_expression")

Examples:
- Simple math: TOOL_CALL: calculate("1000 * 0.05")
- Complex calculations: TOOL_CALL: calculate("(15000 * 0.08) / 12")
- Percentage: TOOL_CALL: calculate("250000 * 0.15")

ALWAYS use the calculator for numerical computations. Do NOT attempt to do math manually.

Example responses:
User: "What's 5% of $10,000?"
You: "I'll calculate that for you. TOOL_CALL: calculate("10000 * 0.05")"

User: "If I invest $5000 at 8% annual return, what's my monthly gain?"
You: "Let me calculate the monthly return on your investment. TOOL_CALL: calculate("5000 * 0.08 / 12")"

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
        try:
            # Check if this might need calculation
            calculation_keywords = ["calculate", "compute", "math", "+", "-", "*", "/", "%", "interest", "profit", "loss", "roi", "return"]
            needs_calculation = any(word in message.lower() for word in calculation_keywords)
            
            if needs_calculation:
                logger.info("Query appears to need calculation, processing with potential tool calls")
            
            # Let the LLM decide if it needs to use tools
            response = await super().process(message, conversation_history)
            
            # Check if response contains tool calls
            if "TOOL_CALL:" in response:
                return await self._handle_tool_calls(response, message, conversation_history)
            
            return response
        except Exception as e:
            logger.error(f"Error in financial agent process: {e}")
            return f"I apologize, but I encountered an error while processing your financial request: {str(e)}"
    
    async def _handle_tool_calls(self, response: str, original_message: str, conversation_history=None) -> str:
        """Handle tool calls in the response."""
        import re
        
        logger.info(f"Processing tool calls in financial response: {response[:200]}...")
        
        # Enhanced regex pattern to capture tool calls
        pattern = r'TOOL_CALL:\s*(\w+)\((.*?)\)'
        matches = re.findall(pattern, response)
        
        if not matches:
            logger.warning("No tool calls found despite TOOL_CALL being in response")
            return response
        
        tool_results = []
        for match in matches:
            tool_name, params = match
            logger.info(f"Attempting to call tool: {tool_name} with params: {params}")
            
            if tool_name in self.tool_map:
                try:
                    # Clean up parameters - remove quotes and whitespace
                    param_value = params.strip().strip('"').strip("'").strip() if params.strip() else ""
                    
                    # Call the tool
                    result = self.tool_map[tool_name].invoke(param_value)
                    logger.info(f"Tool {tool_name} executed successfully with result: {result}")
                    
                    # Format the result nicely
                    if tool_name == 'calculate':
                        if isinstance(result, dict) and 'result' in result:
                            calculation_result = result['result']
                            tool_results.append(f"💰 **Calculation Result:** {param_value} = **{calculation_result}**")
                        else:
                            tool_results.append(f"💰 **Calculation Result:** {param_value} = **{result}**")
                    else:
                        tool_results.append(f"✅ {tool_name} result: {result}")
                        
                except Exception as e:
                    logger.error(f"Error calling tool {tool_name}: {e}")
                    tool_results.append(f"❌ Calculation error: {str(e)}")
            else:
                logger.warning(f"Tool {tool_name} not found in tool_map. Available tools: {list(self.tool_map.keys())}")
                tool_results.append(f"❌ Tool {tool_name} not available")
        
        if tool_results:
            # Create a comprehensive response with tool results
            combined_response = "Here are your financial calculations:\n\n"
            for result in tool_results:
                combined_response += f"{result}\n\n"
            
            # Add financial context and advice
            combined_response += "📊 **Financial Analysis:**\n"
            combined_response += "Based on these calculations, here are some key considerations:\n"
            combined_response += "- Review your financial goals and budget alignment\n"
            combined_response += "- Consider the time value of money in your decisions\n" 
            combined_response += "- Evaluate risk vs. return for any investment scenarios\n"
            combined_response += "- Consult with a qualified financial advisor for personalized advice\n"
            
            return combined_response
        
        return response