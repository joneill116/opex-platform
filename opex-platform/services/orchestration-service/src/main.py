from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os
import asyncpg

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our modules
from src.api_routes import router
from src.engine.core.event_store import EventStore
from src.engine.runtime.workflow_executor import WorkflowExecutor
from src.engine.components.test_components import create_component_registry

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting orchestration-service")
    
    try:
        # Initialize database pool
        app.state.db_pool = await asyncpg.create_pool(
            'postgresql://orchestration:orchestration@postgres-orchestration:5432/orchestration'
        )
        
        # Initialize event store
        app.state.event_store = EventStore(app.state.db_pool)
        await app.state.event_store.initialize()
        
        # Create component registry and executor
        component_registry = create_component_registry()
        app.state.workflow_executor = WorkflowExecutor(
            app.state.event_store,
            component_registry
        )
        
        print("✅ Workflow executor initialized!")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        raise
    
    yield
    
    # Cleanup
    print("Stopping orchestration-service")
    if hasattr(app.state, 'db_pool'):
        await app.state.db_pool.close()

app = FastAPI(
    title="Orchestration Service API",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "service": "orchestration-service",
        "version": "0.1.0",
        "status": "running",
        "endpoints": [
            "/api/v1/workflows",
            "/api/v1/workflows/{id}/execute",
            "/api/v1/executions/{id}",
            "/api/v1/components/types"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
