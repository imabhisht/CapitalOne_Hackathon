#!/usr/bin/env python3
"""
Test script to verify logging configuration works correctly.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app.config import setup_logging, get_logger

def test_logging():
    """Test the logging configuration."""
    # Setup logging
    log_file = setup_logging()
    print(f"Log file created: {log_file}")
    
    # Get loggers for different modules
    main_logger = get_logger("test_main")
    api_logger = get_logger("app.modules.api")
    tools_logger = get_logger("app.modules.tools")
    
    # Test different log levels
    main_logger.debug("This is a debug message")
    main_logger.info("This is an info message")
    main_logger.warning("This is a warning message")
    main_logger.error("This is an error message")
    
    # Test structured logging with extra context
    api_logger.info("API call initiated", extra={"endpoint": "/weather", "method": "GET"})
    tools_logger.info("Tool execution completed", extra={"tool": "get_weather", "duration": "2.3s"})
    
    # Test exception logging
    try:
        raise ValueError("This is a test exception")
    except Exception as e:
        main_logger.error("Test exception caught", exc_info=True)
    
    print("Logging test completed successfully!")
    print(f"Check the log file for details: {log_file}")

if __name__ == "__main__":
    test_logging()
