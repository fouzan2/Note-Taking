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
- **Database Flexibility**: Supports both SQLite and PostgreSQL
- **ORM**: SQLAlchemy with async support for database operations
- **Migrations**: Alembic for database schema versioning
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Type Safety**: Comprehensive type hints and Pydantic validation
- **Testing**: Pytest with async support and fixtures
- **Error Handling**: Custom exception classes with proper HTTP status codes
- **Docker Support**: Full Docker and Docker Compose configuration
- **Production Ready**: Nginx, Gunicorn, and monitoring tools included

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
# Run the setup command to create necessary directories and files
make setup

# Or manually:
cp env.development.example .env.development
cp env.production.example .env.production
```

### 3. Start Development Environment

```bash
# Build and start all services
make up

# Or using docker-compose directly:
docker-compose up -d
```

This will start:
- FastAPI application at http://localhost:8000
- PostgreSQL database
- Redis for caching
- pgAdmin at http://localhost:5050
- Flower (Celery monitoring) at http://localhost:5555

### 4. Run Database Migrations

```bash
make migrate

# Or:
docker-compose exec app alembic upgrade head
```

## 🛠️ Manual Installation (Without Docker)

<details>
<summary>Click to expand manual installation instructions</summary>

### 1. Clone the Repository

```bash
git clone <repository-url>
cd note_taking
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Setup

Create a `.env` file in the project root based on `env.development.example`.

### 5. Database Setup

```bash
# Apply migrations
alembic upgrade head
```

### 6. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

</details>

## 📚 API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## 🔑 Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. **Register a new user**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'
```

2. **Login to get tokens**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=SecurePassword123!"
```

3. **Use the access token in subsequent requests**:
```bash
curl -X GET "http://localhost:8000/api/v1/notes/" \
  -H "Authorization: Bearer <your-access-token>"
```

## 📝 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register a new user | No |
| POST | `/api/v1/auth/login` | Login and get tokens | No |
| GET | `/api/v1/auth/me` | Get current user info | Yes |

### Note Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/notes/` | Create a new note | Yes |
| GET | `/api/v1/notes/` | List all notes (paginated) | Yes |
| GET | `/api/v1/notes/search` | Search notes by query | Yes |
| GET | `/api/v1/notes/{note_id}` | Get specific note | Yes |
| PUT | `/api/v1/notes/{note_id}` | Update a note | Yes |
| DELETE | `/api/v1/notes/{note_id}` | Delete a note | Yes |

### Tag Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/tags/` | List all tags with note counts | Yes |

## 🧪 Testing

### Running Tests with Docker

```bash
# Run all tests
make test

# Or:
docker-compose exec app pytest tests/ -v
```

### Running Tests Locally

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

## 🏗️ Project Structure

```
note_taking/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application initialization
│   ├── core/
│   │   ├── config.py        # Settings and configuration
│   │   ├── security.py      # Authentication and authorization
│   │   └── database.py      # Database connection and session management
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User SQLAlchemy model
│   │   ├── note.py          # Note SQLAlchemy model
│   │   └── tag.py           # Tag SQLAlchemy model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py          # User Pydantic models
│   │   ├── note.py          # Note Pydantic models
│   │   └── tag.py           # Tag Pydantic models
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py          # Dependency injection functions
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py      # Authentication endpoints
│   │       ├── notes.py     # Note management endpoints
│   │       └── tags.py      # Tag management endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py  # Authentication business logic
│   │   ├── note_service.py  # Note management business logic
│   │   └── tag_service.py   # Tag management business logic
│   └── utils/
│       ├── __init__.py
│       └── exceptions.py    # Custom exception classes
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest configuration and fixtures
│   └── test_auth.py         # Authentication tests
├── alembic/
│   ├── env.py               # Alembic environment configuration
│   └── script.py.mako       # Migration template
├── nginx/                   # Nginx configuration
│   ├── nginx.conf
│   └── conf.d/
│       └── app.conf
├── docker-compose.yml       # Development environment
├── docker-compose.prod.yml  # Production environment
├── Dockerfile              # Multi-stage Docker build
├── Makefile               # Convenience commands
├── alembic.ini            # Alembic configuration
├── requirements.txt       # Python dependencies
├── env.development.example # Development environment example
├── env.production.example  # Production environment example
└── README.md              # This file
```

## 🐳 Docker Commands

We provide a Makefile for common Docker operations:

```bash
# Show all available commands
make help

# Development commands
make build          # Build Docker images
make up            # Start development environment
make down          # Stop all containers
make logs          # Show container logs
make shell         # Open shell in app container
make db-shell      # Open PostgreSQL shell
make migrate       # Run database migrations

# Production commands
make prod-build    # Build production images
make prod-up       # Start production environment
make prod-down     # Stop production environment
make prod-logs     # Show production logs

# Utility commands
make clean         # Clean up containers and volumes
make backup        # Create database backup
make restart       # Restart all containers
```

## 🚀 Production Deployment

### Using Docker Compose (Production)

1. **Prepare Production Environment**:

```bash
# Create secrets directory
mkdir -p secrets

# Create secret files (replace with actual values)
echo "prod_user" > secrets/postgres_user.txt
echo "strong_password" > secrets/postgres_password.txt
echo "your-secret-key" > secrets/secret_key.txt
echo "your-jwt-secret" > secrets/jwt_secret.txt
echo "admin" > secrets/grafana_user.txt
echo "admin_password" > secrets/grafana_password.txt
```

2. **Update Production Configuration**:

Edit `.env.production` with your production values.

3. **Start Production Services**:

```bash
# Build and start production services
make prod-up

# Or:
docker-compose -f docker-compose.prod.yml up -d
```

This will start:
- FastAPI application with Gunicorn (4 workers)
- PostgreSQL database
- Redis with persistence
- Nginx reverse proxy
- Celery workers and beat scheduler
- Prometheus monitoring
- Grafana dashboards

### Production Features

- **Load Balancing**: Nginx reverse proxy with rate limiting
- **Security**: Non-root containers, secret management, HTTPS ready
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **Logging**: Structured JSON logging with log rotation
- **Performance**: Multi-worker Gunicorn, connection pooling, caching
- **Reliability**: Health checks, automatic restarts, resource limits

### SSL/HTTPS Configuration

To enable HTTPS in production:

1. Place your SSL certificates in `nginx/ssl/`
2. Uncomment the SSL configuration in `nginx/conf.d/app.conf`
3. Update the server_name with your domain
4. Restart the Nginx container

### 🚄 Railway Deployment

Railway provides a modern, simplified deployment experience. See our detailed [Railway Deployment Guide](RAILWAY_DEPLOYMENT.md) for step-by-step instructions.

**Quick Deploy to Railway:**

1. Push your code to GitHub
2. Connect Railway to your GitHub repo
3. Add PostgreSQL and Redis services
4. Set environment variables:
   ```bash
   # Generate secure key
   openssl rand -hex 32
   ```
5. Deploy! Railway handles the rest

Railway automatically provides:
- HTTPS/SSL certificates
- PostgreSQL and Redis databases
- Automatic deployments from GitHub
- Built-in monitoring and logs
- Easy scaling options

## 💡 Usage Examples

### Creating a Note with Tags

```python
import requests

# Assuming you have a valid access token
headers = {"Authorization": "Bearer <your-access-token>"}

note_data = {
    "title": "My First Note",
    "content": "This is the content of my note.",
    "tags": ["personal", "important", "todo"]
}

response = requests.post(
    "http://localhost:8000/api/v1/notes/",
    json=note_data,
    headers=headers
)

print(response.json())
```

### Searching Notes

```python
# Search for notes containing "important"
params = {"q": "important", "page": 1, "per_page": 20}

response = requests.get(
    "http://localhost:8000/api/v1/notes/search",
    params=params,
    headers=headers
)

results = response.json()
print(f"Found {results['total']} notes")
```

### Filtering Notes by Tag

```python
# Get all notes with the "todo" tag
params = {"tag": "todo", "page": 1, "per_page": 20}

response = requests.get(
    "http://localhost:8000/api/v1/notes/",
    params=params,
    headers=headers
)

notes = response.json()
```

## 🔧 Environment Variables

### Development Environment

Key environment variables for development (see `env.development.example`):

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT signing key
- `DEBUG`: Enable debug mode
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Production Environment

Additional production variables (see `env.production.example`):

- `SENTRY_DSN`: Error tracking with Sentry
- `ENABLE_HTTPS`: Force HTTPS redirects
- `RATE_LIMIT_*`: Rate limiting configuration
- `BACKUP_*`: Automated backup settings

### Railway Environment

Railway-specific variables (see `railway-env.example`):

- Railway provides `DATABASE_URL` and `REDIS_URL` automatically
- `PORT` is dynamically assigned by Railway
- See [Railway Deployment Guide](RAILWAY_DEPLOYMENT.md) for details

## 🔒 Security Considerations

1. **Environment Variables**: Never commit `.env` files with real credentials
2. **Secret Key**: Use a strong, random secret key in production
3. **Password Requirements**: Enforces strong passwords with complexity requirements
4. **HTTPS**: Always use HTTPS in production
5. **Rate Limiting**: Implemented at Nginx level for production
6. **Input Validation**: All inputs are validated using Pydantic models
7. **SQL Injection**: Protected by SQLAlchemy ORM and parameterized queries
8. **Container Security**: Non-root users, minimal base images

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for the powerful ORM
- Pydantic for data validation
- The Python community for amazing tools and libraries 