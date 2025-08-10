"""
Calculator tool for mathematical operations.
"""

from langchain_core.tools import tool
from typing import Union
import logging
import ast
import operator

logger = logging.getLogger(__name__)

# Safe operators for evaluation
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def safe_eval(expression: str) -> Union[float, int]:
    """
    Safely evaluate mathematical expressions.
    """
    try:
        node = ast.parse(expression, mode='eval')
        return _eval_node(node.body)
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")

def _eval_node(node):
    """
    Recursively evaluate AST nodes.
    """
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        op = SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operation: {type(node.op)}")
        return op(left, right)
    elif isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        op = SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operation: {type(node.op)}")
        return op(operand)
    else:
        raise ValueError(f"Unsupported node type: {type(node)}")

@tool
def calculate(expression: str) -> dict:
    """
    Perform mathematical calculations safely.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 3 * 4")
        
    Returns:
        Dict containing the calculation result
    """
    try:
        result = safe_eval(expression)
        
        response = {
            "expression": expression,
            "result": result,
            "success": True
        }
        
        logger.info(f"Calculated: {expression} = {result}")
        return response
        
    except Exception as e:
        logger.error(f"Error calculating {expression}: {e}")
        return {
            "expression": expression,
            "error": str(e),
            "success": False
        }