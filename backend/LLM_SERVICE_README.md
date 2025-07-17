# LLM Service Integration

This document explains how to set up and use the LLM (Large Language Model) service in the Email Agent API.

## Overview

The LLM service provides AI-powered features for email management using **Gemini 2.5 Flash**, the latest and most capable model from Google, including:
- 📧 **Email Content Generation**: Create professional emails from prompts
- 📊 **Sentiment Analysis**: Analyze email tone and sentiment
- 📝 **Subject Line Suggestions**: Generate appropriate email subjects
- 🎯 **Smart Email Composition**: Complete email composition with multiple features
- 💬 **Email Response Generation**: Create appropriate responses to emails
- 💭 **Chat Sessions**: Interactive chat with session management
- 👁️ **Vision Analysis**: Analyze images and documents
- 🛠️ **Tools Integration**: Execute queries with custom tools

## Setup

### 1. Environment Variables

Add the following environment variables to your `.env` file:

```bash
# LLM Configuration
LLM_MODEL_NAME=gemini-2.5-flash
LLM_VISION_MODEL_NAME=gemini-2.5-flash
LLM_PRO_MODEL_NAME=gemini-2.5-pro
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. API Keys Setup

#### Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

**Note**: Gemini 2.5 Flash is the latest and most capable model from Google. Make sure your API key has access to Gemini 2.5 models.

### 3. Install Dependencies

```bash
pip install google-generativeai==0.3.2
```

## API Endpoints

### 1. Generate Email Content
```http
POST /api/llm/generate-email-content
Authorization: Bearer <session_id>
Content-Type: application/json

{
  "prompt": "Write a professional email to schedule a meeting",
  "context": "The recipient is a potential client"
}
```

### 2. Analyze Email Sentiment
```http
POST /api/llm/analyze-email-sentiment
Authorization: Bearer <session_id>
Content-Type: application/json

{
  "email_content": "Your email content here..."
}
```

### 3. Suggest Email Subject
```http
POST /api/llm/suggest-email-subject
Authorization: Bearer <session_id>
Content-Type: application/json

{
  "email_content": "Your email content here...",
  "context": "Optional context about recipient"
}
```

### 4. Enrich Description
```http
POST /api/llm/enrich-description
Authorization: Bearer <session_id>
Content-Type: application/json

{
  "description": "Email automation system"
}
```

### 5. Generate Email Actions
```http
POST /api/llm/generate-email-actions
Authorization: Bearer <session_id>
Content-Type: application/json

{
  "task_description": "Automate follow-up emails",
  "url": "Optional target URL"
}
```

### 6. Smart Email Composer
```http
POST /api/llm/smart-email-composer
Authorization: Bearer <session_id>
Content-Type: application/json

{
  "purpose": "Thank a customer for their purchase",
  "recipient_context": "Customer bought premium software",
  "tone": "grateful",
  "include_subject": true
}
```

### 7. Generate Email Response
```http
POST /api/llm/generate-email-response
Authorization: Bearer <session_id>
Content-Type: application/json

{
  "original_email": "Email to respond to...",
  "response_type": "acknowledge",
  "additional_context": "Optional context"
}
```

### 8. Health Check
```http
GET /api/llm/health
```

## Usage Examples

### Python Code Examples

```python
from app.infrastructure.di.container import get_container

# Get the container and LLM service
container = get_container()
llm_service = container.llm_service()

# Generate email content
content = llm_service.generate_email_content(
    prompt="Write a professional email to schedule a meeting",
    context="The recipient is a potential client"
)

# Analyze sentiment
analysis = llm_service.analyze_email_sentiment(email_content)

# Suggest subject
subject = llm_service.suggest_email_subject(email_content)

# Use cases
generate_content_use_case = container.generate_email_content_use_case()
content = generate_content_use_case.execute(prompt, context)
```

### JavaScript/Frontend Examples

```javascript
// Generate email content
const response = await fetch('/api/llm/generate-email-content', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer your_session_id',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        prompt: 'Write a professional email to schedule a meeting',
        context: 'The recipient is a potential client'
    })
});

const result = await response.json();
console.log(result.content);
```

## Architecture

The LLM service follows clean architecture principles:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  LLM Controller │  │  LLM Models     │  │  LLM Router │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Generate Email  │  │ Analyze Email   │  │ Smart Email │ │
│  │ Content UseCase │  │ Sentiment       │  │ Composer    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    LLM Service                          │ │
│  │  • Gemini Integration                                  │ │
│  │  • Google Custom Search                                │ │
│  │  • Content Generation                                  │ │
│  │  • Sentiment Analysis                                  │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 1. Email Content Generation
- Generate professional emails from natural language prompts
- Support for different tones (professional, casual, formal)
- Context-aware content generation

### 2. Sentiment Analysis
- Analyze email sentiment (positive, negative, neutral)
- Tone detection and analysis
- Professionalism scoring
- Improvement suggestions

### 3. Subject Line Suggestions
- Generate appropriate subject lines
- Context-aware suggestions
- Avoid spam trigger words

### 4. Description Enrichment
- Make descriptions more detailed and actionable
- Add structure and clarity
- Enhance readability

### 5. Email Automation Actions
- Generate automation workflows
- Parse task descriptions into actionable steps
- Support for complex automation scenarios

### 6. Smart Email Composition
- Complete email composition with multiple features
- Generate both content and subject
- Tone and context customization

### 7. Email Response Generation
- Generate appropriate responses to emails
- Support for different response types
- Context-aware response generation

## Error Handling

The LLM service includes comprehensive error handling:

- **API Key Validation**: Ensures all required API keys are present
- **Rate Limiting**: Handles API rate limits gracefully
- **Network Errors**: Retries and fallback mechanisms
- **Invalid Responses**: Fallback to default responses
- **Timeout Handling**: Configurable timeouts for API calls

## Testing

Run the example script to test the LLM service:

```bash
cd backend
python examples/llm_example.py
```

## Monitoring

The LLM service includes health check endpoints:

```bash
curl http://localhost:8000/api/llm/health
```

## Security

- All endpoints require Bearer token authentication
- API keys are stored securely in environment variables
- No sensitive data is logged
- Rate limiting is applied to prevent abuse

## Troubleshooting

### Common Issues

1. **Missing API Keys**
   - Ensure all required environment variables are set
   - Verify API keys are valid and have proper permissions

2. **Rate Limiting**
   - The service includes retry logic for rate limits
   - Consider implementing caching for frequently used requests

3. **Network Issues**
   - Check internet connectivity
   - Verify firewall settings
   - Ensure proxy configuration if applicable

4. **Invalid Responses**
   - The service includes fallback mechanisms
   - Check the logs for detailed error information

### Debug Mode

Enable debug logging by setting:

```bash
DEBUG=true
```

## Performance

- **Caching**: Consider implementing response caching for frequently used prompts
- **Batch Processing**: For multiple requests, consider batching
- **Async Processing**: The service supports async operations for better performance

## Future Enhancements

- [ ] Response caching
- [ ] Batch processing
- [ ] Custom model fine-tuning
- [ ] Multi-language support
- [ ] Advanced prompt templates
- [ ] Integration with more LLM providers

## Support

For issues and questions:
1. Check the logs for detailed error information
2. Verify your API keys and permissions
3. Test with the example script
4. Review the troubleshooting section above 