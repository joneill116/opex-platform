from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ..infrastructure.database import get_db
from ..config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION
    }

@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check including database"""
    try:
        # Check database connection
        await db.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "checks": {
                "database": "connected"
            }
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "checks": {
                "database": f"error: {str(e)}"
            }
        }
