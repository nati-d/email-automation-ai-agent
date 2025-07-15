# Email Agent Backend API

A FastAPI backend application for the Email Agent project.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **Async Support**: Built with async/await for high performance
- **CORS Enabled**: Cross-Origin Resource Sharing configured for frontend integration
- **Environment Configuration**: Flexible configuration using environment variables
- **Health Checks**: Built-in health monitoring endpoints
- **Modular Structure**: Organized codebase with separation of concerns

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

- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key for authentication
- `SMTP_*`: Email server configuration
- `ALLOWED_ORIGINS`: CORS allowed origins

## Next Steps

1. **Database Setup**: Configure your database and create models in `app/models/`
2. **Authentication**: Implement JWT authentication and user management
3. **Email Integration**: Add email processing and sending capabilities
4. **API Endpoints**: Create specific endpoints for your email agent functionality
5. **Background Tasks**: Set up Celery for asynchronous email processing
6. **Testing**: Add comprehensive tests for your API endpoints

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