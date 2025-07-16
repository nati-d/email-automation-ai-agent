# Email Summarization with AI

This document describes the email summarization feature that automatically analyzes and summarizes email content using Google's Gemini AI.

## Overview

When new users sign up and their emails are fetched, the system automatically:
1. **Fetches emails** from Gmail using OAuth
2. **Summarizes content** using Gemini AI
3. **Extracts key information** including main concepts, sentiment, and topics
4. **Stores summarization data** with the email for future reference

## Features

### Automatic Summarization
- **New User Onboarding**: When a new user signs up, their initial emails are automatically summarized
- **Batch Processing**: Multiple emails are processed efficiently with concurrency control
- **Error Handling**: Graceful fallback if summarization fails

### AI Analysis
- **Content Summary**: Concise summary of email content
- **Main Concept**: Primary topic or purpose of the email
- **Sentiment Analysis**: Positive, negative, neutral, or mixed sentiment
- **Key Topics**: Extracted topics and themes from the email

### Manual Summarization
- **Single Email**: Summarize individual emails on-demand
- **Batch Summarization**: Process multiple emails at once
- **Duplicate Prevention**: Skip already summarized emails

## API Endpoints

### 1. Summarize Single Email

**Endpoint**: `POST /api/emails/{email_id}/summarize`

**Authentication**: Bearer token required

**Response**:
```json
{
  "message": "Email summarized successfully",
  "success": true,
  "already_summarized": false,
  "summarization": {
    "summary": "Brief summary of the email content",
    "main_concept": "Primary topic or purpose",
    "sentiment": "positive/negative/neutral/mixed",
    "key_topics": ["topic1", "topic2", "topic3"],
    "summarized_at": "2024-01-01T12:00:00Z"
  }
}
```

### 2. Batch Summarization

**Endpoint**: `POST /api/emails/summarize-batch`

**Authentication**: Bearer token required

**Request Body**: Array of email IDs
```json
["email_id_1", "email_id_2", "email_id_3"]
```

**Response**:
```json
{
  "message": "Batch summarization completed",
  "success": true,
  "total_processed": 3,
  "successful": 2,
  "already_summarized": 1,
  "failed": 0,
  "errors": []
}
```

### 3. Get Emails with Summarization

**Endpoint**: `GET /api/emails`

**Authentication**: Bearer token required

**Response**: Emails now include summarization fields
```json
{
  "emails": [
    {
      "id": "email_id",
      "sender": "sender@example.com",
      "recipients": ["recipient@example.com"],
      "subject": "Email Subject",
      "body": "Email content...",
      "status": "sent",
      "summary": "AI-generated summary",
      "main_concept": "Primary topic",
      "sentiment": "positive",
      "key_topics": ["topic1", "topic2"],
      "summarized_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

## Implementation Details

### Email Entity Updates

The `Email` entity now includes summarization fields:

```python
@dataclass
class Email(BaseEntity):
    # ... existing fields ...
    
    # AI Summarization fields
    summary: Optional[str] = None
    main_concept: Optional[str] = None
    sentiment: Optional[str] = None
    key_topics: List[str] = field(default_factory=list)
    summarized_at: Optional[datetime] = None
```

### LLM Service Integration

The `LLMService` provides email summarization methods:

```python
def summarize_email(
    self,
    email_content: str,
    email_subject: str = "",
    sender: str = "",
    recipient: str = ""
) -> Dict[str, Any]:
    """Summarize email content using Gemini AI"""
```

### Use Cases

#### FetchInitialEmailsUseCase
- Automatically summarizes emails during new user onboarding
- Integrates with Gmail service and LLM service
- Provides detailed logging and error handling

#### SummarizeEmailUseCase
- Handles single email summarization
- Checks for existing summarization to avoid duplicates
- Updates email entity with AI analysis results

#### SummarizeMultipleEmailsUseCase
- Processes multiple emails with concurrency control
- Provides batch statistics and error reporting
- Optimized for performance with configurable concurrency limits

## Configuration

### Environment Variables

```bash
# Required for AI summarization
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Customize LLM model
LLM_MODEL_NAME=gemini-2.5-flash
```

### Settings

The summarization feature uses the following settings:

```python
# LLM Configuration
llm_model_name: str = "gemini-2.5-flash"
llm_vision_model_name: str = "gemini-2.5-flash"
llm_pro_model_name: str = "gemini-2.5-pro"
gemini_api_key: str = "your_api_key"
```

## Usage Examples

### 1. Automatic Summarization (New User)

When a new user signs up through OAuth:

```python
# This happens automatically in ProcessOAuthCallbackUseCase
if is_new_user:
    email_result = await fetch_emails_use_case.execute(
        oauth_token=token,
        user_email=user.email.value,
        limit=50
    )
    # Emails are automatically summarized during import
```

### 2. Manual Single Email Summarization

```python
# Using the API
response = await client.post(
    f"/api/emails/{email_id}/summarize",
    headers={"Authorization": f"Bearer {session_id}"}
)
```

### 3. Batch Summarization

```python
# Using the API
email_ids = ["id1", "id2", "id3"]
response = await client.post(
    "/api/emails/summarize-batch",
    headers={"Authorization": f"Bearer {session_id}"},
    json=email_ids
)
```

### 4. View Summarized Emails

```python
# Get emails with summarization data
response = await client.get(
    "/api/emails",
    headers={"Authorization": f"Bearer {session_id}"}
)

emails = response.json()["emails"]
for email in emails:
    if email.get("summary"):
        print(f"Summary: {email['summary']}")
        print(f"Sentiment: {email['sentiment']}")
```

## Error Handling

### Common Issues

1. **Missing API Key**
   ```
   Error: GEMINI_API_KEY must be set in the .env file
   Solution: Set GEMINI_API_KEY environment variable
   ```

2. **Authentication Required**
   ```
   Error: 401 Unauthorized
   Solution: Provide valid Bearer token in Authorization header
   ```

3. **Email Not Found**
   ```
   Error: Email not found
   Solution: Verify email ID exists and belongs to authenticated user
   ```

4. **LLM Service Unavailable**
   ```
   Error: Failed to connect to Gemini API
   Solution: Check internet connection and API key validity
   ```

### Graceful Degradation

- If summarization fails, email import continues without summarization
- Already summarized emails are skipped to avoid duplicate processing
- Batch operations continue processing other emails if some fail

## Performance Considerations

### Concurrency Control
- Batch summarization uses configurable concurrency limits (default: 5)
- Prevents overwhelming the LLM API with too many simultaneous requests

### Caching
- Summarization results are stored with emails to avoid re-processing
- Check `already_summarized` flag before processing

### Rate Limiting
- Consider Gemini API rate limits for large batch operations
- Implement exponential backoff for failed requests

## Testing

### Example Script

Run the provided example script to test summarization:

```bash
# Set your session ID
export EMAIL_AGENT_SESSION_ID="your_session_id_here"

# Run the example
python examples/email_summarization_example.py
```

### Manual Testing

1. **Start the server**:
   ```bash
   python main.py
   ```

2. **Authenticate** through OAuth flow

3. **Test summarization endpoints**:
   ```bash
   # Summarize single email
   curl -X POST "http://localhost:8000/api/emails/{email_id}/summarize" \
        -H "Authorization: Bearer {session_id}"
   
   # Batch summarization
   curl -X POST "http://localhost:8000/api/emails/summarize-batch" \
        -H "Authorization: Bearer {session_id}" \
        -H "Content-Type: application/json" \
        -d '["email_id_1", "email_id_2"]'
   ```

## Future Enhancements

### Planned Features
- **Custom Summarization Prompts**: Allow users to customize AI analysis
- **Multi-language Support**: Summarize emails in different languages
- **Advanced Analytics**: Email patterns, sender analysis, topic clustering
- **Real-time Summarization**: Summarize emails as they arrive
- **Export Summaries**: Export summarization data in various formats

### Integration Opportunities
- **Email Search**: Search by summary content and key topics
- **Smart Filtering**: Filter emails by sentiment or main concept
- **Automated Responses**: Generate response suggestions based on analysis
- **Email Analytics Dashboard**: Visualize email patterns and insights

## Troubleshooting

### Debug Logging

Enable detailed logging to troubleshoot issues:

```python
# In your application code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Debug Steps

1. **Check API Key**: Verify `GEMINI_API_KEY` is set and valid
2. **Test LLM Service**: Use the health check endpoint
3. **Verify Authentication**: Ensure Bearer token is valid
4. **Check Email Access**: Confirm user has access to the email
5. **Monitor API Limits**: Check Gemini API usage and limits

### Support

For issues with email summarization:
1. Check the application logs for detailed error messages
2. Verify all required environment variables are set
3. Test the LLM service health check endpoint
4. Review the example script for proper usage patterns 