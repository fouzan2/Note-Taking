.PHONY: help build up down logs shell test clean

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start development environment"
	@echo "  make down           - Stop all containers"
	@echo "  make logs           - Show container logs"
	@echo "  make shell          - Open shell in app container"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean up containers and volumes"
	@echo "  make migrate        - Run database migrations"
	@echo "  make db-shell       - Open PostgreSQL shell"
	@echo ""
	@echo "Production (GCP):"
	@echo "  make gcp-setup      - Set up GCP infrastructure"
	@echo "  make gcp-build      - Build production Docker image"
	@echo "  make gcp-deploy     - Deploy to Google Cloud Run"
	@echo "  make gcp-logs       - View Cloud Run logs"
	@echo "  make gcp-migrate    - Run migrations on Cloud SQL"

# Development commands
build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Development environment started!"
	@echo "API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "pgAdmin: http://localhost:5050"
	@echo "Flower: http://localhost:5555"

down:
	docker-compose down

logs:
	docker-compose logs -f

shell:
	docker-compose exec app bash

test:
	docker-compose exec app pytest tests/ -v

migrate:
	docker-compose exec app alembic upgrade head

db-shell:
	docker-compose exec postgres psql -U noteuser -d note_taking_db

# Utility commands
clean:
	docker-compose down -v
	docker system prune -f

restart:
	make down
	make up

# Database backup
backup:
	@echo "Creating database backup..."
	docker-compose exec postgres pg_dump -U noteuser note_taking_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Backup created!"

# Production GCP commands
gcp-setup:
	@echo "Setting up GCP infrastructure..."
	cd deploy && chmod +x setup-gcp.sh && ./setup-gcp.sh

gcp-build:
	@echo "Building production Docker image..."
	docker build -f Dockerfile.production -t gcr.io/$(PROJECT_ID)/note-taking-api:latest .

gcp-push:
	@echo "Pushing image to Google Container Registry..."
	docker push gcr.io/$(PROJECT_ID)/note-taking-api:latest

gcp-deploy:
	@echo "Deploying to Google Cloud Run..."
	cd deploy && chmod +x deploy.sh && ./deploy.sh

gcp-deploy-quick:
	@echo "Quick deploy using Cloud Build..."
	gcloud builds submit --config cloudbuild.yaml

gcp-logs:
	@echo "Viewing Cloud Run logs..."
	gcloud run services logs read note-taking-api --region=$(REGION) --limit=50

gcp-logs-tail:
	@echo "Tailing Cloud Run logs..."
	gcloud run services logs tail note-taking-api --region=$(REGION)

gcp-migrate:
	@echo "Running database migrations on Cloud SQL..."
	gcloud run jobs execute run-migrations --region=$(REGION) --wait

gcp-status:
	@echo "Checking service status..."
	@gcloud run services describe note-taking-api --region=$(REGION) --format="value(status.url)"

gcp-test:
	@echo "Testing production deployment..."
	@SERVICE_URL=$$(gcloud run services describe note-taking-api --region=$(REGION) --format="value(status.url)"); \
	curl -f $$SERVICE_URL/health || exit 1; \
	echo "Health check passed!"

# Set default GCP variables
PROJECT_ID ?= your-gcp-project-id
REGION ?= us-central1 