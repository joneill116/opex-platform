# Runtime Guide for opex-platform

Generated on: 2025-08-03 21:44:33

---

# OpEx Platform - Complete Startup & Shutdown Guide

## 1. Prerequisites Checklist

### Required Software/Tools
- **Docker Desktop** (or Docker Engine + Docker Compose)
  - Version: Docker 20.10+ and Docker Compose 2.0+
  - Verify: `docker --version` and `docker compose version`
- **Node.js** (for frontend development)
  - Version: 20.x
  - Verify: `node --version`
- **Make** (for using Makefile commands)
  - Verify: `make --version`
- **Git** (for cloning repository)
  - Verify: `git --version`

### Environment Setup
1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd opex-platform
   ```

2. **Create environment file**:
   ```bash
   cp infrastructure/docker-compose/.env.template infrastructure/docker-compose/.env
   ```

3. **Edit the .env file** (optional but recommended for production):
   ```bash
   # Edit infrastructure/docker-compose/.env
   # Change at minimum: JWT_SECRET
   ```

## 2. Complete Startup Guide

### Method 1: Using Makefile (Recommended)

1. **Install dependencies**:
   ```bash
   # From project root directory
   make install
   ```
   Expected output: "Installing dependencies..." followed by npm installation logs

2. **Build all services**:
   ```bash
   # From project root directory
   make build
   ```
   Expected output: Docker build logs for each service

3. **Start all services**:
   ```bash
   # From project root directory
   make dev
   ```
   Expected output:
   ```
   Services started! Access points:
   ================================
   Frontend:        http://localhost:3000
   API Gateway:     http://localhost:8000
   Auth Service:    http://localhost:8002
   ```

### Method 2: Manual Docker Compose

1. **Navigate to docker-compose directory**:
   ```bash
   cd infrastructure/docker-compose
   ```

2. **Build services**:
   ```bash
   docker compose build
   ```

3. **Start services in detached mode**:
   ```bash
   docker compose up -d
   ```

4. **Check service status**:
   ```bash
   docker compose ps
   ```

### Startup Order & Dependencies
The services start in this order (handled automatically by Docker Compose):
1. Infrastructure services: PostgreSQL databases, Redis, Zookeeper
2. Kafka (depends on Zookeeper)
3. Jaeger (tracing)
4. Metadata Service
5. Auth Service
6. Orchestration Service (depends on Metadata Service)
7. Kong API Gateway
8. Frontend (if included in compose)

## 3. Service Verification

### Check Running Services
```bash
# From infrastructure/docker-compose directory
docker compose ps

# Or from project root
cd infrastructure/docker-compose && docker compose ps
```

### Service Health Checks

1. **Kong API Gateway**:
   ```bash
   curl http://localhost:8001/status
   ```

2. **Auth Service**:
   ```bash
   curl http://localhost:8002/health
   ```

3. **Metadata Service**:
   ```bash
   curl http://localhost:8007/health
   ```

4. **Orchestration Service**:
   ```bash
   curl http://localhost:8003/health
   ```

5. **Kafka**:
   ```bash
   docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
   ```

6. **PostgreSQL Databases**:
   ```bash
   # Auth DB
   docker compose exec postgres-auth pg_isready -U auth
   
   # Orchestration DB
   docker compose exec postgres-orchestration pg_isready -U orchestration
   
   # Metadata DB
   docker compose exec postgres-metadata pg_isready -U metadata
   ```

7. **Redis**:
   ```bash
   docker compose exec redis redis-cli ping
   # Expected: PONG
   ```

8. **Jaeger UI**:
   - Open browser: http://localhost:16686

### Service URLs & Ports

| Service | Internal Port | External Port | URL |
|---------|--------------|---------------|-----|
| Kong Gateway | 8000 | 8000 | http://localhost:8000 |
| Kong Admin | 8001 | 8001 | http://localhost:8001 |
| Auth Service | 8000 | 8002 | http://localhost:8002 |
| Orchestration Service | 8000 | 8003 | http://localhost:8003 |
| Metadata Service | 8000 | 8007 | http://localhost:8007 |
| PostgreSQL (Auth) | 5432 | 5433 | localhost:5433 |
| PostgreSQL (Orchestration) | 5432 | 5434 | localhost:5434 |
| PostgreSQL (Metadata) | 5432 | 5435 | localhost:5435 |
| Kafka | 9092 | 9092 | localhost:9092 |
| Redis | 6379 | 6379 | localhost:6379 |
| Jaeger UI | 16686 | 16686 | http://localhost:16686 |

## 4. Complete Shutdown Guide

### Method 1: Using Makefile

1. **Stop all services**:
   ```bash
   # From project root directory
   make stop
   ```

2. **Clean up (removes volumes)**:
   ```bash
   # From project root directory
   make clean
   ```

### Method 2: Manual Docker Compose

1. **Stop services (preserves data)**:
   ```bash
   cd infrastructure/docker-compose
   docker compose down
   ```

2. **Stop services and remove volumes (deletes all data)**:
   ```bash
   cd infrastructure/docker-compose
   docker compose down -v
   ```

### Verify Shutdown

1. **Check no containers are running**:
   ```bash
   docker compose ps
   # Should show no running containers
   ```

2. **Check Docker processes**:
   ```bash
   docker ps | grep opex
   # Should return empty
   ```

## 5. Quick Reference

### Common Commands

```bash
# From project root directory

# Start everything
make dev

# View logs
make logs

# Stop everything
make stop

# Clean everything (including data)
make clean

# View specific service logs
cd infrastructure/docker-compose
docker compose logs -f [service-name]
# Example: docker compose logs -f auth-service

# Restart a specific service
cd infrastructure/docker-compose
docker compose restart [service-name]

# Execute command in service
docker compose exec [service-name] [command]
# Example: docker compose exec auth-service /bin/sh
```

### Emergency Shutdown

If services are unresponsive:

```bash
# Force stop all OpEx containers
docker ps | grep opex | awk '{print $1}' | xargs -r docker stop

# Remove all OpEx containers
docker ps -a | grep opex | awk '{print $1}' | xargs -r docker rm -f

# Clean up networks
docker network ls | grep opex | awk '{print $1}' | xargs -r docker network rm
```

### Troubleshooting

1. **Port already in use**:
   ```bash
   # Find process using port (example for port 8000)
   lsof -i :8000  # macOS/Linux
   netstat -ano | findstr :8000  # Windows
   ```

2. **Database connection issues**:
   - Wait 30 seconds after startup for migrations to complete
   - Check logs: `docker compose logs postgres-auth`

3. **Service not starting**:
   ```bash
   # Check specific service logs
   docker compose logs [service-name]
   
   # Rebuild specific service
   docker compose build --no-cache [service-name]
   ```

4. **Frontend not accessible**:
   - Frontend may need separate startup if not in docker-compose
   - Check if running: `docker compose ps | grep frontend`

### Development Workflow

1. **Start services**: `make dev`
2. **Monitor logs**: `make logs` (in separate terminal)
3. **Make changes** to code
4. **Restart affected service**:
   ```bash
   cd infrastructure/docker-compose
   docker compose restart [service-name]
   ```
5. **Stop when done**: `make stop`

---

## Additional Notes

- Always check the repository's README for any updates to these instructions
- If you encounter issues, check log files in the containers/services
- Keep this guide updated as the project evolves

## Guide Generation Details

- Generated using Claude API (claude-opus-4-20250514)
- Based on analysis of Dockerfiles, Makefiles, scripts, and configuration files
- For questions or improvements, regenerate this guide after updating the codebase
