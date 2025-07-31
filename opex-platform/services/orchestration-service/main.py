from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting orchestration-service")
    yield
    print("Stopping orchestration-service")

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

@app.get("/")
async def root():
    return {
        "service": "orchestration-service",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
