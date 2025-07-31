.PHONY: help
help:
	@echo "OpEx Platform - Microservices Commands"
	@echo "======================================"
	@echo "Setup:"
	@echo "  make install          - Install all dependencies"
	@echo "  make build            - Build all services"
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Start all services in development mode"
	@echo "  make stop             - Stop all services"
	@echo "  make logs             - Show logs for all services"
	@echo "  make clean            - Clean up containers and volumes"

.PHONY: install
install:
	@echo "Installing dependencies..."
	cd services/frontend && npm ci

.PHONY: build
build:
	cd infrastructure/docker-compose && docker compose build

.PHONY: dev
dev:
	cd infrastructure/docker-compose && docker compose up -d
	@echo ""
	@echo "Services started! Access points:"
	@echo "================================"
	@echo "Frontend:        http://localhost:3000"
	@echo "API Gateway:     http://localhost:8000"
	@echo "Auth Service:    http://localhost:8002"

.PHONY: stop
stop:
	cd infrastructure/docker-compose && docker compose down

.PHONY: logs
logs:
	cd infrastructure/docker-compose && docker compose logs -f

.PHONY: clean
clean:
	cd infrastructure/docker-compose && docker compose down -v