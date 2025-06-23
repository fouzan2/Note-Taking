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