# Email Agent Backend API

A FastAPI backend application for the Email Agent project.

## Features

- **Email Management**: Send, receive, and manage emails
- **AI-Powered Summarization**: Automatic email summarization using Google Gemini
- **Email Categorization**: Intelligent categorization of emails as inbox or tasks
- **OAuth Authentication**: Secure Google OAuth integration
- **Multiple Account Support**: Add multiple email accounts to a single user account
- **Email Categories**: User-defined categories for inbox organization
- **Real-time Processing**: Asynchronous email processing and AI analysis

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py          # Application configuration
│   ├── models/            # Database models
│   ├── routers/           # API route handlers
│   │   ├── __init__.py
│   │   └── health.py      # Health check endpoints
│   └── schemas/           # Pydantic schemas
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables example
└── README.md             # This file
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Setup

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` file with your specific configuration values.

### 3. Run the Application

```bash
# Using Python directly
python main.py

# Or using uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the API

- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## API Endpoints

### Health Checks

- `GET /api/health` - Basic health check
- `GET /api/health/detailed` - Detailed health information

### Authentication

- `GET /api/auth/google/login` - Initiate Google OAuth login
- `GET /api/auth/google/callback` - Handle OAuth callback
- `GET /api/auth/me` - Get current user info (requires Bearer token)
- `POST /api/auth/refresh` - Refresh OAuth token (requires Bearer token)
- `POST /api/auth/logout` - Logout and revoke tokens (requires Bearer token)

### Email Management

- `GET /api/emails` - Get user's emails (requires Bearer token)
- `POST /api/emails/send` - Send email (requires Bearer token)

### AI Email Summarization

- `POST /api/emails/{email_id}/summarize` - Summarize single email (requires Bearer token)
- `POST /api/emails/summarize-batch` - Summarize multiple emails in batch (requires Bearer token)

### LLM Services

- `GET /api/llm/health` - LLM service health check
- `POST /api/llm/generate` - Generate content using Gemini AI
- `POST /api/llm/chat` - Start chat session
- `POST /api/llm/chat/{session_id}/message` - Send message to chat session
- `POST /api/llm/email/write` - Generate email content
- `POST /api/llm/email/analyze` - Analyze email sentiment
- `POST /api/llm/email/suggest-subject` - Suggest email subject line

### Core Endpoints

- `GET /` - Welcome message

## Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables auto-reloading when code changes are detected.

### Environment Variables

Key environment variables (see `.env.example` for full list):

- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret
- `GOOGLE_REDIRECT_URI`: OAuth redirect URI
- `GEMINI_API_KEY`: Google Gemini AI API key (required for email summarization)
- `FRONTEND_URL`: Frontend application URL
- `SMTP_*`: Email server configuration
- `ALLOWED_ORIGINS`: CORS allowed origins

## Next Steps

1. **OAuth Setup**: Configure Google OAuth credentials in Google Cloud Console
2. **Gemini API**: Get a Gemini API key for email summarization features
3. **Email Configuration**: Set up SMTP settings for email sending
4. **Testing**: Test the OAuth flow and email summarization features
5. **Frontend Integration**: Connect your frontend application to the API
6. **Production Deployment**: Deploy to production with proper security settings

## Documentation

- [OAuth Authentication Guide](docs/BEARER_TOKEN_AUTH.md)
- [Email Sending Guide](docs/EMAIL_SENDING_GUIDE.md)
- [Email Summarization Guide](docs/EMAIL_SUMMARIZATION.md)
- [LLM Service Documentation](docs/LLM_SERVICE.md)

## Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation and serialization
- **SQLAlchemy**: Database ORM
- **Alembic**: Database migrations
- **Redis**: Caching and message broker
- **Celery**: Background task processing

## Production Deployment

For production deployment, consider:

1. Using a production ASGI server like Gunicorn with Uvicorn workers
2. Setting up a reverse proxy (Nginx)
3. Configuring environment variables securely
4. Setting up database and Redis instances
5. Implementing logging and monitoring 