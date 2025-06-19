# Multi-stage Dockerfile for FastAPI Note Taking Application

# Base stage with common dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user with specific UID/GID for development
RUN groupadd -r -g 1000 appuser && useradd -r -u 1000 -g appuser appuser

# Development stage
FROM base as development

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

USER appuser

# Expose port (will be overridden by Railway)
EXPOSE 8000

# Development command with auto-reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production build stage
FROM base as builder

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base as production

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

USER appuser

# Expose port (will be overridden by Railway's PORT env var)
EXPOSE 8000

# Production command that respects Railway's PORT environment variable
# Railway will override this command in railway.toml
CMD gunicorn app.main:app -w ${RAILWAY_REPLICA_COUNT:-4} -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --access-logfile - --error-logfile - --timeout 120 --keep-alive 5 --max-requests 1000 --max-requests-jitter 50 