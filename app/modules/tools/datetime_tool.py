"""
Date/time tool for getting current date and time.
"""
from datetime import datetime
from typing import Dict
from ...config import get_logger

# Initialize logger
logger = get_logger(__name__)

def tool_get_date_time() -> Dict:
    logger.info("Tool called: get_date_time")
    
    try:
        now = datetime.now()
        result = {
            "success": True,
            "dateFormat": "%Y-%m-%d %H:%M:%S",
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "timestamp": now.timestamp(),
            "timezone": str(now.astimezone().tzinfo),
            "source": "system"
        }
        
        logger.debug(f"Current date/time: {result['date']} {result['time']} ({result['timezone']})")
        logger.info("Date/time data successfully retrieved")
        
        return result
    except Exception as e:
        logger.error(f"Error getting date/time: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Error getting date/time: {str(e)}"
        }