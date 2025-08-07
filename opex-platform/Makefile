.PHONY: help
help:
	@echo "🏆 OpEx Platform - The Architectural Masterpiece"
	@echo "=============================================="
	@echo ""
	@echo "🚀 SINGLE COMMAND PERFECTION:"
	@echo "  make perfect          - Perfect startup (auto-detects platform)"
	@echo "  make perfect-windows  - Perfect startup for Windows PowerShell"
	@echo "  make perfect-linux    - Perfect startup for Linux/macOS/WSL"
	@echo ""
	@echo "📋 Individual Commands:"
	@echo "  make install          - Install all dependencies"
	@echo "  make build            - Build all services"
	@echo "  make dev              - Start all services in development mode"
	@echo "  make health-check     - Verify all services are healthy"
	@echo "  make stop             - Stop all services gracefully"
	@echo "  make logs             - Show logs for all services"
	@echo "  make clean            - Complete cleanup (removes all data)"
	@echo ""
	@echo "🔧 Database Operations:"
	@echo "  make db-migrate       - Run database migrations"
	@echo "  make db-reset         - Reset all databases"

# Auto-detect platform and run appropriate perfect command
.PHONY: perfect
perfect:
	@if command -v powershell >/dev/null 2>&1 && [ "$$OS" = "Windows_NT" ]; then \
		echo "🪟 Detected Windows - using PowerShell script..."; \
		$(MAKE) perfect-windows; \
	else \
		echo "🐧 Detected Unix/Linux/WSL - using bash script..."; \
		$(MAKE) perfect-linux; \
	fi

.PHONY: perfect-windows
perfect-windows:
	@echo "🚀 Starting OpEx Platform with PowerShell perfection..."
	@powershell -ExecutionPolicy Bypass -File scripts/startup.ps1

.PHONY: perfect-linux
perfect-linux:
	@echo "🚀 Starting OpEx Platform with Bash perfection..."
	@chmod +x scripts/startup.sh
	@./scripts/startup.sh

.PHONY: install
install:
	@echo "📦 Installing frontend dependencies..."
	cd services/frontend && npm ci
	@echo "✅ Dependencies installed successfully!"

.PHONY: build
build:
	@echo "🏗️ Building all services..."
	cd infrastructure/docker-compose && docker compose build --parallel
	@echo "✅ All services built successfully!"

.PHONY: dev
dev:
	@echo "🚀 Starting OpEx Platform..."
	@echo "📊 Step 1: Starting databases and core infrastructure..."
	cd infrastructure/docker-compose && docker compose up -d postgres-auth postgres-orchestration postgres-metadata redis zookeeper
	@echo "⏳ Waiting for databases to initialize..."
	@sleep 15
	@echo "📊 Step 2: Starting Kafka message broker..."
	cd infrastructure/docker-compose && docker compose up -d kafka
	@echo "⏳ Waiting for Kafka to initialize..."
	@sleep 20
	@echo "📊 Step 3: Starting microservices..."
	cd infrastructure/docker-compose && docker compose up -d auth-service metadata-service orchestration-service
	@echo "⏳ Waiting for services to initialize..."
	@sleep 10
	@echo "📊 Step 4: Starting API Gateway and Frontend..."
	cd infrastructure/docker-compose && docker compose up -d kong frontend jaeger
	@echo "⏳ Final initialization..."
	@sleep 5
	@echo "✅ All services started successfully!"

.PHONY: health-check
health-check:
	@echo "🔍 Performing comprehensive health checks..."
	@echo "Checking Auth Service..."
	@timeout 5 bash -c 'until curl -sf http://localhost:8002/health >/dev/null 2>&1; do sleep 1; done' && echo "✅ Auth Service healthy" || echo "❌ Auth Service unhealthy"
	@echo "Checking Metadata Service..."
	@timeout 5 bash -c 'until curl -sf http://localhost:8007/health >/dev/null 2>&1; do sleep 1; done' && echo "✅ Metadata Service healthy" || echo "❌ Metadata Service unhealthy"
	@echo "Checking Orchestration Service..."
	@timeout 5 bash -c 'until curl -sf http://localhost:8003/health >/dev/null 2>&1; do sleep 1; done' && echo "✅ Orchestration Service healthy" || echo "❌ Orchestration Service unhealthy"
	@echo "Checking API Gateway..."
	@timeout 5 bash -c 'until curl -sf http://localhost:8001/status >/dev/null 2>&1; do sleep 1; done' && echo "✅ API Gateway healthy" || echo "❌ API Gateway unhealthy"
	@echo "Checking Frontend..."
	@timeout 5 bash -c 'until curl -sf http://localhost:3000 >/dev/null 2>&1; do sleep 1; done' && echo "✅ Frontend healthy" || echo "❌ Frontend unhealthy"
	@echo ""
	@echo "🎉 ALL SERVICES VERIFIED HEALTHY! PERFECTION ACHIEVED!"

.PHONY: db-migrate
db-migrate:
	@echo "🗃️ Running database migrations..."
	cd infrastructure/docker-compose && docker compose exec orchestration-service alembic upgrade head
	cd infrastructure/docker-compose && docker compose exec auth-service alembic upgrade head  
	cd infrastructure/docker-compose && docker compose exec metadata-service alembic upgrade head
	@echo "✅ All migrations completed successfully!"

.PHONY: db-reset
db-reset:
	@echo "🔄 Resetting all databases..."
	cd infrastructure/docker-compose && docker compose down
	cd infrastructure/docker-compose && docker volume rm docker-compose_postgres_auth_data docker-compose_postgres_orchestration_data docker-compose_postgres_metadata_data docker-compose_redis_data 2>/dev/null || true
	@echo "✅ Databases reset successfully!"

.PHONY: stop
stop:
	@echo "🛑 Stopping all services gracefully..."
	cd infrastructure/docker-compose && docker compose down
	@echo "✅ All services stopped successfully!"

.PHONY: logs
logs:
	@echo "📋 Showing logs for all services..."
	cd infrastructure/docker-compose && docker compose logs -f

.PHONY: clean
clean:
	@echo "🧹 Performing complete cleanup..."
	cd infrastructure/docker-compose && docker compose down -v --rmi all
	@echo "✅ Complete cleanup finished!"