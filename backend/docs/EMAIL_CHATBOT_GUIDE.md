# Email Chatbot Guide

## Overview

The Email Chatbot is an intelligent AI-powered assistant that provides comprehensive information about your emails. It uses advanced natural language processing and function calling to understand your queries and provide detailed insights about your email data.

## Features

### 🔍 **Smart Email Search**
- Search by sender, recipient, subject, content, category, and date range
- Natural language queries like "Show me emails from John about project updates"
- Advanced filtering with multiple criteria

### 📊 **Email Analytics & Statistics**
- Comprehensive email statistics and trends
- Breakdown by category, sender, time periods
- Sentiment analysis overview
- Email activity patterns

### 📝 **Detailed Email Analysis**
- Individual email insights with summaries
- Sentiment analysis and key topics
- Relationship mapping between emails
- Context-aware responses

### 🔗 **Related Email Discovery**
- Find emails related to specific topics
- Conversation thread analysis
- Sender relationship mapping
- Topic-based email clustering

### ⏰ **Recent Activity Tracking**
- Real-time email activity monitoring
- Important email identification
- Recent conversation summaries
- Pending item tracking

## API Endpoints

### 1. Get Email Chatbot Information

**Endpoint:** `GET /llm/email-chatbot/info`

**Description:** Get information about the email chatbot capabilities.

**Response:**
```json
{
  "message": "Email chatbot ready for user@example.com. I can help you analyze your emails, find specific messages, get statistics, and provide insights. What would you like to know about your emails?",
  "capabilities": [
    "Search emails by sender, recipient, subject, content, category, and date",
    "Get detailed email analysis with summaries and sentiment",
    "Generate email statistics and trends",
    "Find related emails and conversation threads",
    "Track recent email activity and important items"
  ]
}
```

### 2. Chat with Email Bot

**Endpoint:** `POST /llm/email-chatbot/chat`

**Description:** Chat with the email intelligence bot to get information about your emails.

**Request:**
```json
{
  "message": "Show me all emails from john@example.com"
}
```

**Response:**
```json
{
  "message": "Found 5 emails from john@example.com:\n\n📧 ID: email_123\n   From: john@example.com\n   Subject: Project Update - Q1 Results\n   Date: 2024-01-15 14:30\n   Category: Work\n   Summary: John provided Q1 project results with positive metrics...",
  "success": true,
  "tools_used": ["search_emails"]
}
```

## Example Queries

### Basic Search Queries
```
"Show me all emails from john@example.com"
"What are my recent work emails?"
"Find emails about project updates"
"Show me emails from this week"
"Find emails with attachments"
```

### Statistical Queries
```
"Give me statistics for this month"
"What's my email activity like?"
"Show me breakdown by category"
"Who sends me the most emails?"
"What's my sentiment analysis?"
```

### Analysis Queries
```
"Find emails related to budget discussions"
"Show me conversation threads with Sarah"
"What are my most important emails?"
"Find emails about the quarterly review"
"Show me emails that need follow-up"
```

### Activity Queries
```
"What's my recent email activity?"
"Show me important emails from today"
"What emails did I miss?"
"Find urgent emails"
"Show me recent conversations"
```

## Available Tools

The chatbot uses several AI-powered tools to provide comprehensive email analysis:

### 1. **search_emails**
- **Purpose:** Search and filter emails by various criteria
- **Parameters:**
  - `query`: Search query for subject or content
  - `sender`: Filter by sender email address
  - `recipient`: Filter by recipient email address
  - `category`: Filter by email category
  - `email_type`: Filter by email type (inbox/sent)
  - `date_from`/`date_to`: Date range filtering
  - `limit`: Maximum number of emails to return

### 2. **get_email_details**
- **Purpose:** Get detailed information about a specific email
- **Parameters:**
  - `email_id`: The ID of the email to analyze
- **Returns:** Summary, sentiment, key topics, and full content

### 3. **get_email_statistics**
- **Purpose:** Generate statistical overview of emails
- **Parameters:**
  - `period`: Time period (today/week/month/quarter/year/all)
  - `include_sentiment`: Include sentiment analysis
- **Returns:** Counts, categories, senders, sentiment breakdown

### 4. **find_related_emails**
- **Purpose:** Find emails related to specific topics or senders
- **Parameters:**
  - `topic`: Topic or keyword to search for
  - `sender`: Sender email to find related emails from
  - `subject_keyword`: Keyword in subject line
  - `limit`: Maximum number of related emails

### 5. **get_recent_activity**
- **Purpose:** Get recent email activity and important items
- **Parameters:**
  - `hours`: Number of hours to look back
  - `include_summaries`: Include email summaries
- **Returns:** Recent emails with context and importance

## Authentication

All email chatbot endpoints require authentication using a Bearer token:

```
Authorization: Bearer your_session_id_here
```

The session ID is obtained from the OAuth login process and represents the user's authenticated session.

## Usage Examples

### Python Example

```python
import requests

# Get chatbot info
response = requests.get(
    "http://localhost:8000/llm/email-chatbot/info",
    headers={"Authorization": "Bearer your_session_id"}
)
info = response.json()
print(f"Capabilities: {info['capabilities']}")

# Send a query
response = requests.post(
    "http://localhost:8000/llm/email-chatbot/chat",
    headers={"Authorization": "Bearer your_session_id"},
    json={
        "message": "Show me my recent work emails"
    }
)
print(response.json()["message"])
```

### JavaScript Example

```javascript
// Get chatbot info
const infoResponse = await fetch('/llm/email-chatbot/info', {
    method: 'GET',
    headers: {
        'Authorization': 'Bearer your_session_id'
    }
});
const info = await infoResponse.json();
console.log('Capabilities:', info.capabilities);

// Send a query
const chatResponse = await fetch('/llm/email-chatbot/chat', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer your_session_id',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        message: 'Show me my recent work emails'
    })
});
const result = await chatResponse.json();
console.log(result.message);
```

## Best Practices

### 1. **Stateless Design**
- No session management required - each request is independent
- No need to start or end sessions
- Each query is processed fresh with full context

### 2. **Query Optimization**
- Be specific in your queries for better results
- Use natural language rather than technical terms
- Combine multiple criteria for precise filtering

### 3. **Error Handling**
- Check response status codes
- Handle authentication errors gracefully
- Implement retry logic for transient failures

### 4. **Performance**
- Limit the number of emails returned for large datasets
- Use date ranges to narrow down searches
- Cache frequently requested data when possible

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure you have a valid session ID from OAuth login
   - Check that the Bearer token is properly formatted
   - Verify the session hasn't expired

2. **No Results Found**
   - Try broader search criteria
   - Check if emails exist for the specified time period
   - Verify the user has access to the requested emails

3. **Tool Execution Errors**
   - Check if the email repository is accessible
   - Verify user permissions for email access
   - Ensure the LLM service is properly configured

### Debug Information

The chatbot provides detailed logging for debugging:

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Existing Features

The email chatbot integrates seamlessly with your existing email system:

- **Email Summarization**: Uses existing AI-generated summaries
- **Sentiment Analysis**: Leverages existing sentiment data
- **Categorization**: Works with your email categories
- **User Profiles**: Incorporates user communication style
- **OAuth Authentication**: Uses existing session management

## Future Enhancements

Planned improvements for the email chatbot:

1. **Real-time Notifications**: Alert users about important emails
2. **Email Scheduling**: Help schedule follow-up emails
3. **Meeting Detection**: Identify emails that should become meetings
4. **Priority Scoring**: Automatically score email importance
5. **Multi-language Support**: Support for multiple languages
6. **Voice Integration**: Voice-based email queries
7. **Mobile Optimization**: Enhanced mobile experience
8. **Advanced Analytics**: More sophisticated email insights

## Support

For questions or issues with the email chatbot:

1. Check the troubleshooting section above
2. Review the API documentation
3. Test with the provided example scripts
4. Check server logs for detailed error information
5. Ensure all dependencies are properly configured 