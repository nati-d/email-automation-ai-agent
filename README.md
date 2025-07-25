# Email Agent Backend API

A FastAPI backend application for email automation and processing.

## 🏗️ Project Structure

```
email-agent/
├── app/
│   ├── routers/            # API route handlers
│   │   ├── __init__.py
│   │   └── health.py      # Health check endpoints
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── config.py          # Application configuration
│   └── __init__.py
├── main.py                # FastAPI entry point
├── run.py                 # Development server runner
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Git** for version control

### 1. Clone the Repository

```bash
git clone https://github.com/nati-d/email-automation-ai-agent.git
cd email-automation-ai-agent
```

### 2. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env
# Edit .env with your configuration
```

### 3. Run the Application

```bash
# Using Python directly
python main.py

# Or using uvicorn with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using the run script
python run.py
```

**API will be available at:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/api/health

## 🛠️ Development

### Running in Development Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables auto-reloading when code changes are detected.

### Environment Variables

Key environment variables (see `env.example` for full list):

- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key for authentication
- `SMTP_*`: Email server configuration
- `ALLOWED_ORIGINS`: CORS allowed origins

## 📋 Available Scripts

- `python main.py` - Start the FastAPI server
- `python run.py` - Start with configuration from settings
- `uvicorn main:app --reload` - Development server with auto-reload

## 🔧 Configuration

Environment variables are configured in `.env`:

- `DATABASE_URL` - Database connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT secret key
- `SMTP_*` - Email server settings
- `ALLOWED_ORIGINS` - CORS origins

## 🗄️ Database

The backend supports multiple databases through SQLAlchemy:

- **Development:** SQLite (default)
- **Production:** PostgreSQL (recommended)

## 📚 API Endpoints

### Health Checks

- `GET /api/health` - Basic health check
- `GET /api/health/detailed` - Detailed health information

### Core Endpoints

- `GET /` - Welcome message

## 🚀 Deployment

### Using Railway, Heroku, or DigitalOcean

1. Set environment variables in your deployment platform
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

## 🧪 Testing

```bash
pytest
```

## 📚 API Documentation

When the backend is running, visit:
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:

1. Review the API documentation at `/docs`
2. Check the logs for error messages
3. Verify environment variables are set correctly
4. Open an issue in the repository
