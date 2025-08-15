# Smart Routing System

## Overview

The Smart Routing System automatically routes user requests to the most appropriate LLM model based on the complexity of the task. This helps speed up responses for simple queries while ensuring complex tasks get the full power of the main model.

## How It Works

### 1. Request Classification
The system analyzes incoming messages and classifies them as either:
- **Simple**: Greetings, basic questions, short responses
- **Complex**: Analysis, calculations, detailed explanations, code generation

### 2. Model Selection
- **Small/Fast Model**: Used for simple tasks (faster response, lower cost)
- **Main Model**: Used for complex tasks (more capable, slower)

### 3. Routing Decision Factors
- **Message length**: Short messages → Small model
- **Keywords**: Complex keywords → Main model  
- **Patterns**: Common greetings/responses → Small model
- **Question complexity**: Simple questions → Small model, detailed questions → Main model

## Configuration

### Environment Variables

```bash
# Main LLM (for complex tasks)
LLM_MODEL=z-ai/glm-4.5-air:free
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://openrouter.ai/api/v1

# Small LLM (for simple tasks and routing)
SMALL_LLM_MODEL=openai/gpt-3.5-turbo
SMALL_LLM_API_KEY=your_api_key
SMALL_LLM_BASE_URL=https://openrouter.ai/api/v1

# Enable/disable smart routing
USE_SMART_ROUTING=true
```

### Model Recommendations

**For Small/Fast Model:**
- `openai/gpt-3.5-turbo` - Fast and reliable
- `anthropic/claude-3-haiku` - Very fast, good for simple tasks
- `meta-llama/llama-3.1-8b-instruct` - Good balance of speed and capability

**For Main Model:**
- `z-ai/glm-4.5-air:free` - Good general purpose model
- `anthropic/claude-3.5-sonnet` - Excellent for complex reasoning
- `openai/gpt-4` - High capability for complex tasks

## API Endpoints

### Analyze Routing Decision
```bash
POST /routing/analyze
Content-Type: application/json

{
  "message": "Hello, how are you?"
}
```

Response:
```json
{
  "message": "Hello, how are you?",
  "routing_decision": {
    "message_length": 18,
    "word_count": 4,
    "classification": "simple",
    "confidence": 0.9,
    "use_small_llm": true,
    "selected_model": "small"
  },
  "models": {
    "small_model": "openai/gpt-3.5-turbo",
    "main_model": "z-ai/glm-4.5-air:free"
  }
}
```

## Testing

Run the routing test script:

```bash
cd backend
python test_routing.py
```

This will show you how different types of messages are classified and routed.

## Examples

### Simple Messages (→ Small Model)
- "Hello"
- "Thank you"
- "What time is it?"
- "How are you?"
- "Yes" / "No"

### Complex Messages (→ Main Model)
- "Analyze the financial implications of different mortgage options"
- "Write a Python function to calculate compound interest"
- "Explain machine learning algorithms"
- "Help me create a business plan"
- "Compare investment strategies"

## Benefits

1. **Faster Responses**: Simple queries get answered quickly
2. **Cost Optimization**: Use cheaper models for simple tasks
3. **Better Resource Utilization**: Reserve powerful models for complex tasks
4. **Improved User Experience**: Reduced latency for common interactions

## Monitoring

The Streamlit UI includes a routing analyzer in the sidebar where you can:
- Test routing decisions for any message
- See classification confidence scores
- View which model would be selected
- Monitor routing performance

## Customization

You can customize the routing logic by modifying `src/services/routing_service.py`:

- Add new simple patterns
- Modify complexity keywords
- Adjust confidence thresholds
- Add custom classification rules

## Troubleshooting

### Common Issues

1. **All requests go to main model**: Check if `USE_SMART_ROUTING=true` in .env
2. **Routing service errors**: Verify small model credentials are correct
3. **No speed improvement**: Ensure small model is actually faster than main model

### Debug Mode

Set logging level to INFO to see routing decisions:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

You'll see logs like:
```
INFO:src.services.chat_service:Using small LLM for message: Hello...
INFO:src.services.routing_service:Routing info: {'classification': 'simple', 'confidence': 0.9, 'use_small_llm': True}
```