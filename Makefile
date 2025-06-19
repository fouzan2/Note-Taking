.PHONY: help build up down logs shell test clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start development environment"
	@echo "  make down           - Stop all containers"
	@echo "  make logs           - Show container logs"
	@echo "  make shell          - Open shell in app container"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean up containers and volumes"
	@echo "  make prod-up        - Start production environment"
	@echo "  make prod-down      - Stop production environment"
	@echo "  make migrate        - Run database migrations"
	@echo "  make db-shell       - Open PostgreSQL shell"

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

# Production commands
prod-up:
	docker-compose -f docker-compose.prod.yml up -d
	@echo "Production environment started!"

prod-down:
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

prod-build:
	docker-compose -f docker-compose.prod.yml build

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

# Create required directories and files
setup:
	@echo "Setting up project..."
	@mkdir -p secrets
	@mkdir -p nginx/ssl
	@mkdir -p monitoring
	@cp env.development.example .env.development
	@cp env.production.example .env.production
	@echo "Setup complete! Please update .env.development and .env.production files." 