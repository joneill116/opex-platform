"""
ENTERPRISE HEALTH CHECK UTILITY
Standardized health checks across all services following SRE best practices.
"""

from typing import Dict, Any, List, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio
import time

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"  
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    duration_ms: float
    details: Dict[str, Any]
    timestamp: datetime

class EnterpriseHealthChecker:
    """
    Centralized health checking following Google SRE patterns.
    Provides consistent health reporting across all services.
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.checks: Dict[str, Callable] = {}
        self.startup_time = time.time()
    
    def register_check(self, name: str, check_func: Callable) -> None:
        """Register a health check function"""
        self.checks[name] = check_func
    
    async def run_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        results = []
        overall_status = HealthStatus.HEALTHY
        
        for name, check_func in self.checks.items():
            start_time = time.time()
            try:
                if asyncio.iscoroutinefunction(check_func):
                    details = await check_func()
                else:
                    details = check_func()
                
                status = HealthStatus.HEALTHY
                duration_ms = (time.time() - start_time) * 1000
                
            except Exception as e:
                details = {"error": str(e)}
                status = HealthStatus.UNHEALTHY
                duration_ms = (time.time() - start_time) * 1000
                overall_status = HealthStatus.UNHEALTHY
            
            results.append(HealthCheck(
                name=name,
                status=status,
                duration_ms=duration_ms,
                details=details,
                timestamp=datetime.utcnow()
            ))
        
        # Calculate uptime
        uptime_seconds = time.time() - self.startup_time
        
        return {
            "service": self.service_name,
            "status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": uptime_seconds,
            "checks": [
                {
                    "name": check.name,
                    "status": check.status.value,
                    "duration_ms": check.duration_ms,
                    "details": check.details,
                    "timestamp": check.timestamp.isoformat()
                }
                for check in results
            ]
        }

# Standard health check functions
async def database_health_check(db_pool) -> Dict[str, Any]:
    """Standard database connectivity check"""
    async with db_pool.acquire() as conn:
        await conn.fetchval("SELECT 1")
    return {"status": "connected", "pool_size": db_pool.get_size()}

def memory_health_check() -> Dict[str, Any]:
    """Standard memory usage check"""
    import psutil
    memory = psutil.virtual_memory()
    return {
        "usage_percent": memory.percent,
        "available_mb": memory.available // 1024 // 1024,
        "total_mb": memory.total // 1024 // 1024
    }
