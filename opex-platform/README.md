# Runtime & Database Setup Guide for opex-platform

Generated on: 2025-08-03 22:34:32

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

## 2. Database Initialization Guide (CRITICAL)

### Database Schema Issues
Based on the repository analysis, there's a critical issue with the database migrations:

1. **The `workflow_events` table is defined in migration files but may not be automatically applied**
2. **Migration file exists at**: `services/orchestration-service/migrations/002_event_store_fixed.sql`

### Manual Database Initialization Steps

1. **Start only the database services first**:
   ```bash
   cd infrastructure/docker-compose
   docker compose up -d postgres-auth postgres-orchestration postgres-metadata
   ```

2. **Wait for databases to be ready** (about 10 seconds):
   ```bash
   # Check if databases are ready
   docker compose exec postgres-orchestration pg_isready -U orchestration
   docker compose exec postgres-auth pg_isready -U auth
   docker compose exec postgres-metadata pg_isready -U metadata
   ```

3. **Apply the workflow_events table migration manually**:
   ```bash
   # Copy the migration file to the container
   docker compose cp ../../services/orchestration-service/migrations/002_event_store_fixed.sql postgres-orchestration:/tmp/

   # Execute the migration
   docker compose exec postgres-orchestration psql -U orchestration -d orchestration -f /tmp/002_event_store_fixed.sql
   ```

4. **Verify the tables were created**:
   ```bash
   # Check if workflow_events table exists
   docker compose exec postgres-orchestration psql -U orchestration -d orchestration -c "\dt"
   
   # You should see:
   # - workflow_events
   # - execution_snapshots
   ```

## 3. Complete Startup Guide

### Method 1: Step-by-Step Startup (Recommended for First Time)

1. **From the project root directory**:
   ```bash
   # Install frontend dependencies
   make install
   ```

2. **Build all Docker images**:
   ```bash
   make build
   ```

3. **Start infrastructure services first**:
   ```bash
   cd infrastructure/docker-compose
   
   # Start databases, Redis, Zookeeper
   docker compose up -d postgres-auth postgres-orchestration postgres-metadata redis zookeeper
   
   # Wait 10 seconds for initialization
   sleep 10
   ```

4. **Apply database migrations manually** (as shown in section 2 above)

5. **Start Kafka** (needs Zookeeper to be running):
   ```bash
   docker compose up -d kafka
   
   # Wait for Kafka to initialize (important!)
   sleep 15
   
   # Verify Kafka is ready
   docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
   ```

6. **Start remaining services**:
   ```bash
   # Start all other services
   docker compose up -d
   
   # Check all services are running
   docker compose ps
   ```

### Method 2: Quick Start (After Initial Setup)

Once databases are initialized with tables:
```bash
# From project root
make dev

# Or from docker-compose directory
cd infrastructure/docker-compose
docker compose up -d
```

## 4. Service Verification

### Check All Services Status
```bash
cd infrastructure/docker-compose
docker compose ps

# All services should show "running" status
```

### Health Check URLs

1. **Orchestration Service** (Port 8003):
   ```bash
   curl http://localhost:8003/health
   # Expected: {"status":"healthy","service":"orchestration-service"}
   ```

2. **Auth Service** (Port 8002):
   ```bash
   curl http://localhost:8002/health
   # Expected: {"status":"healthy","service":"auth-service"}
   ```

3. **Metadata Service** (Port 8007):
   ```bash
   curl http://localhost:8007/health
   # Expected: {"status":"healthy","service":"metadata-service"}
   ```

4. **Kong API Gateway**:
   ```bash
   curl http://localhost:8001/status
   # Expected: JSON with Kong status
   ```

### Verify Database Tables
```bash
# Check orchestration database tables
docker compose exec postgres-orchestration psql -U orchestration -d orchestration -c "\dt"

# Should show:
# - workflow_events
# - execution_snapshots
# - alembic_version (if migrations ran)
```

## 5. Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: "workflow_events table does not exist"
**Solution**:
```bash
# Stop the orchestration service
docker compose stop orchestration-service

# Apply the migration manually
docker compose exec postgres-orchestration psql -U orchestration -d orchestration -f /tmp/002_event_store_fixed.sql

# Restart the service
docker compose start orchestration-service
```

#### Issue 2: Kafka connection errors
**Solution**:
```bash
# Restart Kafka and Zookeeper
docker compose restart zookeeper kafka

# Wait 20 seconds
sleep 20

# Verify Kafka is accessible
docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```

#### Issue 3: Service crashes on startup
**Check logs**:
```bash
# View logs for specific service
docker compose logs -f orchestration-service

# View last 100 lines
docker compose logs --tail=100 orchestration-service
```

### Reset Everything (Fresh Start)
```bash
# Stop all services and remove volumes
cd infrastructure/docker-compose
docker compose down -v

# Remove all images
docker compose down --rmi all

# Start fresh
cd ../..
make build
make dev
```

## 6. Complete Shutdown Guide

### Graceful Shutdown (Preserves Data)
```bash
# From project root
make stop

# Or manually
cd infrastructure/docker-compose
docker compose down
```

### Complete Cleanup (Removes All Data)
```bash
# From project root
make clean

# Or manually
cd infrastructure/docker-compose
docker compose down -v
```

### Verify Shutdown
```bash
# Check no containers are running
docker ps | grep opex
# Should return empty

# Check networks are removed
docker network ls | grep opex
# Should return empty
```

## 7. Quick Reference

### Database Commands
```bash
# Connect to orchestration database
docker compose exec postgres-orchestration psql -U orchestration -d orchestration

# List all tables
\dt

# Describe workflow_events table
\d workflow_events

# Exit psql
\q
```

### Service Management
```bash
# Start all services
make dev

# Stop all services
make stop

# View logs
make logs

# Restart specific service
cd infrastructure/docker-compose
docker compose restart orchestration-service

# View specific service logs
docker compose logs -f orchestration-service
```

### Health Check URLs
- Orchestration: `http://localhost:8003/health`
- Auth: `http://localhost:8002/health`
- Metadata: `http://localhost:8007/health`
- Kong Status: `http://localhost:8001/status`
- Jaeger UI: `http://localhost:16686`

### Port Reference
| Service | Port | Purpose |
|---------|------|---------|
| 8000 | Kong Gateway | API Gateway |
| 8001 | Kong Admin | Gateway Admin |
| 8002 | Auth Service | Authentication |
| 8003 | Orchestration | Workflow Management |
| 8007 | Metadata | Metadata Service |
| 5433 | PostgreSQL Auth | Auth Database |
| 5434 | PostgreSQL Orchestration | Orchestration Database |
| 5435 | PostgreSQL Metadata | Metadata Database |
| 9092 | Kafka | Message Broker |
| 6379 | Redis | Cache |
| 16686 | Jaeger | Tracing UI |

### Emergency Commands
```bash
# Force stop all containers
docker stop $(docker ps -q | grep opex)

# Remove all opex containers
docker rm -f $(docker ps -a -q | grep opex)

# Clean up everything
docker system prune -a --volumes
```

## Important Notes

1. **First-time setup requires manual database migration** for the workflow_events table
2. **Kafka needs 15-20 seconds to initialize** before other services can connect
3. **Services have dependencies** - databases must be running before application services
4. **The frontend is not included in docker-compose** - run separately with `npm run dev` in services/frontend
5. **Default credentials** are in the docker-compose.yml file - change for production use

---

## Additional Notes

- Always run database migrations BEFORE starting services
- If you get "table does not exist" errors, check the Database Initialization section above
- Kafka needs 30-60 seconds to fully initialize - be patient
- Always check the repository's README for any updates to these instructions
- If you encounter issues, check log files: `docker compose logs [service-name]`
- Keep this guide updated as the project evolves

## Common Issues

### orchestration-service fails with "workflow_events table does not exist"
- This means database migrations haven't been run
- Follow the Database Initialization steps above
- Make sure postgres-orchestration is running first

### Kafka connection refused
- Kafka takes time to start (30-60 seconds)
- Ensure zookeeper is running first
- Check logs: `docker compose logs kafka`

### Port 8003 not accessible
- Check if orchestration-service is running: `docker compose ps orchestration-service`
- View logs for errors: `docker compose logs orchestration-service`
- Ensure all dependencies are running first

## Guide Generation Details

- Generated using Claude API (claude-opus-4-20250514)
- Based on analysis of Dockerfiles, Makefiles, scripts, migration files, and configuration files
- For questions or improvements, regenerate this guide after updating the codebase
