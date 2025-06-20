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
- **Docker Support**: Full Docker and Docker Compose configuration for local development

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
# Copy the development environment example
cp .env.development.example .env.development
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
- Flower (Celery web UI) at http://localhost:5555

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

Create a `.env.development` file in the project root based on `.env.development.example`.

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
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── config.py        # Settings and configuration
│   │   │   ├── security.py      # Authentication and authorization
│   │   │   └── database.py      # Database connection and session management
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # User SQLAlchemy model
│   │   │   ├── note.py          # Note SQLAlchemy model
│   │   │   └── tag.py           # Tag SQLAlchemy model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py          # User Pydantic models
│   │   │   ├── note.py          # Note Pydantic models
│   │   │   └── tag.py           # Tag Pydantic models
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py          # Dependency injection functions
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py      # Authentication endpoints
│   │   │       ├── notes.py     # Note management endpoints
│   │   │       └── tags.py      # Tag management endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py  # Authentication business logic
│   │   │   ├── note_service.py  # Note management business logic
│   │   │   └── tag_service.py   # Tag management business logic
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── exceptions.py    # Custom exception classes
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Pytest configuration and fixtures
│   │   └── test_auth.py         # Authentication tests
│   ├── alembic/
│   │   ├── env.py               # Alembic environment configuration
│   │   └── script.py.mako       # Migration template
│   ├── deploy/                  # GCP deployment files
│   │   ├── setup-gcp.sh         # Infrastructure setup script
│   │   ├── deploy.sh            # Deployment script
│   │   ├── cloud-run-service.yaml # Cloud Run configuration
│   │   ├── env.production.example # Production environment example
│   │   └── README.md            # Deployment documentation
│   ├── .github/
│   │   └── workflows/
│   │       └── deploy-gcp.yml   # GitHub Actions deployment workflow
│   ├── docker-compose.yml       # Development environment
│   ├── Dockerfile               # Development Docker image
│   ├── Dockerfile.production    # Production Docker image
│   ├── cloudbuild.yaml         # Google Cloud Build configuration
│   ├── Makefile                # Convenience commands
│   ├── alembic.ini            # Alembic configuration
│   ├── requirements.txt       # Python dependencies
│   ├── requirements-prod.txt  # Production dependencies (without Celery)
│   ├── .env.development.example # Development environment example
│   └── README.md              # This file
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

# Utility commands
make clean         # Clean up containers and volumes
make backup        # Create database backup
make restart       # Restart all containers
```

## ☁️ Google Cloud Platform Deployment

The application is optimized for deployment to Google Cloud Run with Cloud SQL and Memorystore Redis.

### Prerequisites

- Google Cloud account with billing enabled
- `gcloud` CLI installed and configured
- Docker installed locally

### Quick Deployment

1. **Set up GCP infrastructure**:
   ```bash
   export PROJECT_ID=your-gcp-project-id
   export REGION=us-central1
   make gcp-setup
   ```

2. **Deploy the application**:
   ```bash
   make gcp-deploy
   ```

3. **View deployment status**:
   ```bash
   make gcp-status
   ```

### Production Features

- **Auto-scaling**: Scales from 1 to 10 instances based on load
- **Managed services**: Uses Cloud SQL for PostgreSQL and Memorystore for Redis
- **Security**: Secrets stored in Google Secret Manager
- **CI/CD**: GitHub Actions workflow for automatic deployments
- **Monitoring**: Integrated with Google Cloud Logging and monitoring

### GCP Commands

```bash
# GCP deployment commands
make gcp-setup       # Set up GCP infrastructure
make gcp-build       # Build production Docker image
make gcp-deploy      # Deploy to Google Cloud Run
make gcp-logs        # View Cloud Run logs
make gcp-migrate     # Run migrations on Cloud SQL
make gcp-status      # Check service status
make gcp-test        # Test production deployment
```

### Cost Optimization

The deployment is configured for cost efficiency:
- Cloud Run bills only for actual usage
- Minimum 1 instance to avoid cold starts
- Optimized container size for faster scaling
- Proper resource limits to prevent overuse

For detailed deployment instructions, see [deploy/README.md](deploy/README.md).

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

Key environment variables for development (see `.env.development.example`):

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT signing key
- `DEBUG`: Enable debug mode
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## 🔒 Security Considerations

1. **Environment Variables**: Never commit `.env` files with real credentials
2. **Secret Key**: Use a strong, random secret key
3. **Password Requirements**: Enforces strong passwords with complexity requirements
4. **Input Validation**: All inputs are validated using Pydantic models
5. **SQL Injection**: Protected by SQLAlchemy ORM and parameterized queries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📊 Code Coverage with Codecov

To enable code coverage reporting in GitHub Actions:

1. **Sign up for Codecov**:
   - Go to [codecov.io](https://codecov.io)
   - Sign in with your GitHub account
   - Add your repository

2. **Get your Codecov token**:
   - In Codecov, go to your repository settings
   - Copy the repository upload token

3. **Add token to GitHub Secrets**:
   - Go to your GitHub repository settings
   - Navigate to Settings > Secrets and variables > Actions
   - Click "New repository secret"
   - Name: `CODECOV_TOKEN`
   - Value: Your Codecov token from step 2

4. **Push changes**:
   - The workflow is already configured to use the token
   - Coverage reports will now upload successfully without rate limiting

> **Note**: The workflow has been updated with `fail_ci_if_error: false` temporarily. Once you add the `CODECOV_TOKEN` secret, you can change this back to `true` in `.github/workflows/deploy-gcp.yml` to ensure coverage uploads are working correctly.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for the powerful ORM
- Pydantic for data validation
- The Python community for amazing tools and libraries 