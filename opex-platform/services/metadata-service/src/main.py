from fastapi import FastAPI

app = FastAPI(title="Metadata Service")

@app.get("/")
async def root():
    return {"service": "metadata-service", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
