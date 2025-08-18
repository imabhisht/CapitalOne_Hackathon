# Logging Implementation Guide

## Overview
This application now includes comprehensive logging at every step of the process. All logs are written to both the console and timestamped log files in the `logs/` directory.

## Logging Features

### 1. **Structured Logging**
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s`
- **File Logging**: All debug-level and above messages
- **Console Logging**: Info-level and above messages
- **Log Files**: Timestamped files in `logs/app_YYYYMMDD_HHMMSS.log`

### 2. **Module-Specific Loggers**
Each module has its own logger for better traceability:
- `streamlit_app.py`: Main application flow
- `app.modules.api`: OpenRouter API calls and tool handling
- `app.modules.tools`: Weather API calls and location services
- `app.modules.prompts`: System prompt generation
- `app.modules.ui`: UI component rendering

### 3. **Log Levels Used**
- **DEBUG**: Detailed information for development and troubleshooting
- **INFO**: General application flow and important events
- **WARNING**: Potentially problematic situations
- **ERROR**: Error conditions that don't stop the application

## What's Being Logged

### Main Application (`streamlit_app.py`)
- Application startup and configuration
- User prompt processing
- Chat history management
- Location status updates
- API call orchestration
- Tool execution iterations
- Response streaming

### API Module (`app/modules/api.py`)
- OpenRouter API call details (parameters, response metadata)
- Tool call processing and execution
- Error handling and recovery
- Tool response formatting

### Tools Module (`app/modules/tools.py`)
- Weather API requests and responses
- Browser location retrieval
- Date/time tool execution
- Network error handling
- Data validation

### Prompts Module (`app/modules/prompts.py`)
- System prompt generation
- Tool schema processing
- Location context integration

### UI Module (`app/modules/ui.py`)
- Location permission components
- Response streaming progress
- Component rendering

## Log File Examples

### Typical Startup Sequence
```
2024-08-18 10:30:15,123 - streamlit_app - INFO - <module>:15 - Starting Smart Location-Aware Assistant v1.0.0
2024-08-18 10:30:15,124 - streamlit_app - INFO - <module>:16 - Log file: /path/to/logs/app_20240818_103015.log
2024-08-18 10:30:15,125 - streamlit_app - INFO - <module>:17 - OpenRouter Model: anthropic/claude-3-sonnet
2024-08-18 10:30:15,126 - streamlit_app - INFO - <module>:18 - API Keys configured - OpenRouter: Yes, Weather: Yes
```

### User Query Processing
```
2024-08-18 10:31:22,456 - streamlit_app - INFO - <module>:89 - User prompt received: What's the weather like here?
2024-08-18 10:31:22,457 - app.modules.prompts - DEBUG - generate_system_prompt:15 - Generating system prompt
2024-08-18 10:31:22,458 - app.modules.api - DEBUG - openrouter_tools_schema:25 - Generating OpenRouter tools schema
2024-08-18 10:31:22,459 - app.modules.api - INFO - call_openrouter_chat:65 - Making API call to OpenRouter with model: anthropic/claude-3-sonnet
```

### Tool Execution
```
2024-08-18 10:31:23,789 - app.modules.api - INFO - handle_tool_calls:102 - Processing 2 tool calls
2024-08-18 10:31:23,790 - app.modules.api - INFO - handle_tool_calls:125 - Executing tool: get_lat_lon_from_browser
2024-08-18 10:31:23,791 - app.modules.tools - INFO - tool_get_lat_lon_from_browser:85 - Tool called: get_lat_lon_from_browser
2024-08-18 10:31:23,792 - app.modules.tools - INFO - tool_get_weather_by_coords:15 - Getting weather data for coordinates: 37.7749, -122.4194
```

## Testing Logging

Run the test script to verify logging is working:
```bash
python test_logging.py
```

This will:
1. Create a new log file
2. Test all log levels
3. Test structured logging
4. Test exception logging
5. Display the log file location

## Log File Management

- Log files are automatically timestamped
- Old log files are not automatically deleted (implement rotation if needed)
- Logs directory is in `.gitignore` to avoid committing sensitive data
- Each application run creates a new log file

## Environment Variables Impact on Logging

The logging configuration respects environment settings:
- Missing API keys are logged as warnings
- Configuration issues are logged with appropriate severity
- Network errors include full exception details

## Troubleshooting with Logs

1. **Application won't start**: Check the first few lines of the latest log file
2. **API errors**: Search for "OpenRouter API" or "WeatherAPI" in logs
3. **Tool failures**: Look for tool execution logs with ERROR level
4. **Location issues**: Search for "location" or "browser" in logs
5. **Performance issues**: Track timestamps between log entries

## Best Practices

1. **Log Review**: Regularly review logs for errors and warnings
2. **Log Retention**: Implement log rotation if disk space is a concern
3. **Sensitive Data**: Logs avoid logging sensitive data like API keys
4. **Debugging**: Use DEBUG level logs for detailed troubleshooting
5. **Monitoring**: Set up alerts for ERROR level logs in production
