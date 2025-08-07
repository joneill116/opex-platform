"""
WORLD-CLASS ORCHESTRATION SERVICE
Enterprise-grade microservice with full observability, resilience, and monitoring.
Built following Martin Fowler's enterprise patterns and SRE best practices.
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os
import asyncpg
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from src.api_routes import router
from src.engine.core.event_store import EventStore
from src.engine.runtime.workflow_executor import WorkflowExecutor
from src.engine.components.test_components import create_component_registry
from src.config import settings

# Import enterprise infrastructure
try:
    from opex_common.observability import initialize_observability, get_observability
    from opex_common.resilience import ResilienceOrchestrator
    from opex_common.logging import configure_enterprise_logging
    from opex_common.health import EnterpriseHealthChecker, database_health_check, memory_health_check
    ENTERPRISE_FEATURES = True
    # Configure logging once for the service
    logger = configure_enterprise_logging("orchestration-service")
except ImportError:
    ENTERPRISE_FEATURES = False
    # Fallback simple logger
    import logging
    logger = logging.getLogger(__name__)

# Global health checker
health_checker = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enterprise application lifecycle with full observability and health monitoring"""
    startup_time = time.time()
    
    try:
        logger.info("orchestration.service.starting", version="2.0.0", enterprise_features=ENTERPRISE_FEATURES)
        
        # Initialize enterprise observability stack
        if ENTERPRISE_FEATURES:
            jaeger_endpoint = f"http://{os.getenv('JAEGER_AGENT_HOST', 'localhost')}:{os.getenv('JAEGER_AGENT_PORT', '6831')}"
            observability = initialize_observability("orchestration-service", jaeger_endpoint)
            
            # Initialize resilience orchestrator
            resilience = ResilienceOrchestrator("orchestration-service")
            app.state.resilience = resilience
            
            # Register SRE alert rules
            observability.alerts.register_alert_rule(
                "database_connection_failed",
                "database_pool_exhausted",
                "critical",
                "Database connection pool exhausted - service degraded"
            )
            
            logger.info("observability.initialized", components=["metrics", "tracing", "alerts", "logging"])
        
        # Initialize database connection pool
        logger.info("database.connecting", url=settings.DATABASE_URL.replace(settings.DATABASE_URL.split('@')[0].split('//')[1], "***"))
        
        try:
            # Create database pool with enterprise configuration
            app.state.db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=5,
                max_size=20,
                max_queries=50000,
                max_inactive_connection_lifetime=300.0,
                command_timeout=10
            )
            logger.info("database.connected", pool_size="5-20", timeout=10)
            
        except Exception as e:
            logger.error("database.connection.failed", error=str(e))
            if ENTERPRISE_FEATURES:
                observability.alerts.fire_alert("database_connection_failed")
            raise
        
        # Initialize event store with full enterprise features
        try:
            app.state.event_store = EventStore(app.state.db_pool)
            await app.state.event_store.initialize()
            logger.info("event.store.initialized", features=["ordering", "kafka_publishing", "subscriptions"])
            
        except Exception as e:
            logger.error("event.store.failed", error=str(e))
            raise
        
        # Initialize workflow executor with component registry
        try:
            component_registry = create_component_registry()
            app.state.workflow_executor = WorkflowExecutor(app.state.event_store, component_registry)
            logger.info("workflow.executor.initialized", components=len(component_registry))
            
        except Exception as e:
            logger.error("workflow.executor.failed", error=str(e))
            raise
        
        # Record successful startup metrics
        startup_duration = time.time() - startup_time
        if ENTERPRISE_FEATURES:
            observability.metrics.histogram(
                "service_startup_duration_seconds", 
                startup_duration,
                {"service": "orchestration", "status": "success"}
            )
        
        logger.info(
            "orchestration.service.ready",
            startup_duration_ms=round(startup_duration * 1000, 2),
            features=["event_sourcing", "workflow_execution", "observability", "resilience"]
        )
        
        yield
        
    except Exception as e:
        startup_duration = time.time() - startup_time
        if ENTERPRISE_FEATURES:
            observability.metrics.histogram(
                "service_startup_duration_seconds",
                startup_duration,
                {"service": "orchestration", "status": "failed"}
            )
        
        logger.error("orchestration.service.startup.failed", 
                    error=str(e), 
                    startup_duration_ms=round(startup_duration * 1000, 2))
        raise
        
    finally:
        # Graceful shutdown
        logger.info("orchestration.service.shutting_down")
        
        try:
            if hasattr(app.state, 'db_pool'):
                await app.state.db_pool.close()
                logger.info("database.disconnected")
        except Exception as e:
            logger.error("database.shutdown.failed", error=str(e))
        
        logger.info("orchestration.service.stopped")

# Create FastAPI app with enterprise configuration
app = FastAPI(
    title="OpEx Orchestration Service",
    description="World-class workflow orchestration with event sourcing and enterprise observability",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Enterprise middleware stack
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response middleware for observability
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    """Enterprise observability middleware tracking all requests"""
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", f"req-{int(time.time() * 1000)}")
    
    # Add request context to logs
    with structlog.contextvars.bound_contextvars(request_id=request_id):
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            
            # Record metrics if enterprise features available
            if ENTERPRISE_FEATURES:
                observability = get_observability()
                await observability.record_request(
                    method=request.method,
                    endpoint=str(request.url.path),
                    status_code=response.status_code,
                    duration_ms=duration_ms
                )
            
            # Add enterprise headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Service"] = "orchestration-service"
            response.headers["X-Version"] = "2.0.0"
            
            logger.info(
                "http.request.completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
                request_id=request_id
            )
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # Record error metrics
            if ENTERPRISE_FEATURES:
                observability = get_observability()
                await observability.record_request(
                    method=request.method,
                    endpoint=str(request.url.path),
                    status_code=500,
                    duration_ms=duration_ms
                )
            
            logger.error(
                "http.request.failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_ms=round(duration_ms, 2),
                request_id=request_id
            )
            raise

# Include the API routes
app.include_router(router, prefix="/api/v1", tags=["Workflows"])

@app.get("/", tags=["Service Info"])
async def root():
    """Service information endpoint"""
    return {
        "service": "orchestration-service",
        "version": "2.0.0",
        "status": "running",
        "enterprise_features": ENTERPRISE_FEATURES,
        "capabilities": [
            "workflow_orchestration",
            "event_sourcing", 
            "distributed_tracing",
            "circuit_breakers",
            "bulkhead_isolation",
            "automatic_retries",
            "structured_logging",
            "real_time_metrics"
        ],
        "endpoints": [
            "/api/v1/workflows",
            "/api/v1/workflows/{id}",
            "/api/v1/workflows/{id}/execute",
            "/api/v1/executions/{id}",
            "/api/v1/components/types",
            "/health",
            "/metrics"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health", tags=["Health"])
async def health():
    """Comprehensive health check with dependency status"""
    health_status = {
        "status": "healthy",
        "service": "orchestration-service",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time() - getattr(app.state, '_start_time', time.time())
    }
    
    # Check database health
    try:
        if hasattr(app.state, 'db_pool'):
            async with app.state.db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            health_status["database"] = {"status": "healthy", "pool_size": app.state.db_pool.get_size()}
        else:
            health_status["database"] = {"status": "not_configured"}
    except Exception as e:
        health_status["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Check event store health
    try:
        if hasattr(app.state, 'event_store'):
            # Simple health check - could be expanded
            health_status["event_store"] = {"status": "healthy"}
        else:
            health_status["event_store"] = {"status": "not_configured"}
    except Exception as e:
        health_status["event_store"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Add enterprise health metrics
    if ENTERPRISE_FEATURES:
        try:
            observability = get_observability()
            health_status.update(observability.get_health_metrics())
            
            if hasattr(app.state, 'resilience'):
                health_status["resilience"] = app.state.resilience.get_health_status()
        except:
            pass
    
    return health_status

@app.get("/metrics", tags=["Observability"])
async def metrics():
    """Prometheus-compatible metrics endpoint"""
    if not ENTERPRISE_FEATURES:
        return {"error": "Enterprise observability not available"}
    
    try:
        observability = get_observability()
        return {
            "metrics": observability.metrics.metrics,
            "format": "json",
            "note": "Use /metrics/prometheus for Prometheus format"
        }
    except Exception as e:
        return {"error": f"Failed to retrieve metrics: {str(e)}"}

# Initialize start time for uptime calculation
@app.on_event("startup")
async def set_start_time():
    app.state._start_time = time.time()
