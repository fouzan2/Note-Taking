# Note Taking API

A robust and scalable RESTful API for managing personal notes with tag support, built with FastAPI and SQLAlchemy. This API allows users to create, read, update, and delete notes with associated tags for organization, featuring user authentication and comprehensive search capabilities.

## 🚀 Features

### Core Features
- **Note Management (CRUD)**: Create, read, update, and delete personal notes
- **Tag Support**: Organize notes with tags using many-to-many relationships
- **User Authentication**: JWT-based authentication with secure password hashing
- **Search Functionality**: Search notes by title or content
- **Tag Filtering**: Filter notes by specific tags
- **Pagination**: Efficient pagination for large datasets

### Technical Features
- **Async/Await**: Full async support for optimal performance
- **Database Support**: PostgreSQL with SQLAlchemy async ORM
- **Migrations**: Alembic for database schema versioning
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Type Safety**: Comprehensive type hints and Pydantic validation
- **Testing**: Pytest with async support and fixtures
- **Error Handling**: Custom exception classes with proper HTTP status codes
- **Docker Support**: Full Docker and Docker Compose configuration
- **Redis Caching**: Redis for session storage and caching

## 📋 Requirements

- Docker and Docker Compose (recommended)
- OR Python 3.9+ with PostgreSQL and Redis

## 🐳 Quick Start with Docker (Recommended)

The easiest way to get started is using Docker and Docker Compose:

### 1. Clone the Repository

```bash
git clone <repository-url>
cd note_taking
```

### 2. Setup Environment

```bash
# The .env.development file is already configured for Docker
# You can modify it if needed
```

### 3. Start Development Environment

```bash
# Build and start all services
make up

# Or manually with docker-compose
docker-compose up -d
```

This will start:
- **FastAPI application** on http://localhost:8000
- **PostgreSQL database** on localhost:5432
- **Redis** on localhost:6379
- **pgAdmin** on http://localhost:5050

### 4. Verify Installation

```bash
# Check if all services are running
docker-compose ps

# View logs
make logs

# Test the API
curl http://localhost:8000/health
```

### 5. Access the API

- **API Documentation**: http://localhost:8000/api/v1/docs
- **Alternative Docs**: http://localhost:8000/api/v1/redoc
- **Health Check**: http://localhost:8000/health
- **pgAdmin**: http://localhost:5050 (admin@example.com / admin)

## 📚 API Usage

### Authentication

First, create a user account and get an access token:

```bash
# Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'

# Login to get access token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "testpass123"}'
```

### Notes Management

```bash
# Create a note (use the access token from login)
curl -X POST "http://localhost:8000/api/v1/notes/" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title": "My First Note", "content": "This is the content", "tags": ["personal", "important"]}'

# Get all notes
curl -X GET "http://localhost:8000/api/v1/notes/" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Search notes
curl -X GET "http://localhost:8000/api/v1/notes/search?q=first" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by tags
curl -X GET "http://localhost:8000/api/v1/notes/?tags=personal" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🛠️ Development

### Available Commands

```bash
# Development commands
make help            # Show all available commands
make build           # Build Docker images
make up              # Start development environment
make down            # Stop all containers
make logs            # Show container logs
make shell           # Open shell in app container
make test            # Run tests
make migrate         # Run database migrations
make db-shell        # Open PostgreSQL shell
make clean           # Clean up containers and volumes
make restart         # Restart all services
```

### Database Management

```bash
# Run migrations
make migrate

# Access database shell
make db-shell

# Create a new migration
docker-compose exec app alembic revision --autogenerate -m "Description"
```

### Testing

The project includes authentication tests. However, tests are excluded from the Docker container by `.dockerignore`.

To run tests:

```bash
# Option 1: Run tests locally
pip install -r requirements.txt
pytest tests/ -v

# Option 2: Temporarily enable tests in Docker
# 1. Comment out 'tests/' line in .dockerignore
# 2. Rebuild the container: make build
# 3. Run tests: make test
```

### Code Quality

```bash
# Format code with Black
docker-compose exec app black app tests

# Check types with mypy
docker-compose exec app mypy app

# Lint with flake8
docker-compose exec app flake8 app tests
```

## 📁 Project Structure

```
note_taking/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py              # Dependency injection
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── notes.py         # Note CRUD endpoints
│   │       └── tags.py          # Tag management endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Application configuration
│   │   ├── database.py          # Database connection and session
│   │   ├── redis.py             # Redis connection and utilities
│   │   └── security.py          # Authentication and security utilities
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User SQLAlchemy model
│   │   ├── note.py              # Note SQLAlchemy model
│   │   └── tag.py               # Tag SQLAlchemy model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py              # User Pydantic schemas
│   │   ├── note.py              # Note Pydantic schemas
│   │   └── tag.py               # Tag Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Authentication business logic
│   │   ├── note_service.py      # Note management business logic
│   │   └── tag_service.py       # Tag management business logic
│   └── utils/
│       ├── __init__.py
│       └── exceptions.py        # Custom exception classes
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration and fixtures
│   └── test_auth.py             # Authentication tests
├── alembic/
│   ├── env.py                   # Alembic environment configuration
│   └── versions/                # Database migration files
├── nginx/                       # Nginx configuration
│   └── conf.d/
├── docker-compose.yml           # Development environment
├── Dockerfile                   # Application Docker image
├── Makefile                     # Convenience commands
├── alembic.ini                  # Alembic configuration
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── test_api_curl.sh            # API testing script
├── API_TEST_RESULTS.md         # API test results documentation
├── .env.development             # Development environment variables
├── .dockerignore               # Docker ignore patterns
├── .gitignore                  # Git ignore patterns
└── README.md                    # Project documentation
```

## 🔧 Configuration

### Environment Variables

Key environment variables for development (`.env.development`):

```bash
# Database
DATABASE_URL=postgresql+asyncpg://noteuser:notepassword@postgres:5432/note_taking_db

# Redis
REDIS_URL=redis://:redispassword@redis:6379/0

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for secure password storage
- **Input Validation**: Pydantic models for request validation
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **CORS Configuration**: Configurable cross-origin resource sharing
- **Rate Limiting**: Built-in rate limiting support
- **Security Headers**: HTTP security headers

## 📊 Monitoring and Health Checks

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

Returns status of:
- API server
- PostgreSQL database
- Redis cache

### Logs

```bash
# View all logs
make logs

# View specific service logs
docker-compose logs -f app
docker-compose logs -f postgres
docker-compose logs -f redis
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for the powerful ORM
- Pydantic for data validation
- Alembic for database migrations
- Docker for containerization
- PostgreSQL for the database
- Redis for caching and session storage 