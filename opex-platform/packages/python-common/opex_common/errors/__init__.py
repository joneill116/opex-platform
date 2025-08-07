"""
ENTERPRISE ERROR HANDLING
Centralized error handling and formatting across all services.
Follows RFC 7807 Problem Details standard.
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from dataclasses import dataclass
import traceback
import uuid
from datetime import datetime

@dataclass
class ErrorContext:
    """Rich error context for debugging and monitoring"""
    error_id: str
    timestamp: datetime
    service_name: str
    endpoint: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    stack_trace: Optional[str] = None

class EnterpriseErrorHandler:
    """
    Centralized error handling following RFC 7807 Problem Details standard.
    Provides consistent error responses across all services.
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
    
    def create_error_response(
        self,
        status_code: int,
        title: str,
        detail: str,
        error_type: str = "about:blank",
        instance: Optional[str] = None,
        context: Optional[ErrorContext] = None
    ) -> Dict[str, Any]:
        """Create RFC 7807 compliant error response"""
        
        error_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        response = {
            "type": error_type,
            "title": title,
            "status": status_code,
            "detail": detail,
            "instance": instance,
            "error_id": error_id,
            "timestamp": timestamp.isoformat(),
            "service": self.service_name
        }
        
        if context:
            response["context"] = {
                "request_id": context.request_id,
                "user_id": context.user_id,
                "endpoint": context.endpoint
            }
            
            # Only include stack trace in development
            if context.stack_trace and self.service_name.endswith("-dev"):
                response["debug"] = {
                    "stack_trace": context.stack_trace
                }
        
        return response
    
    async def handle_http_exception(
        self, 
        request: Request, 
        exc: HTTPException
    ) -> JSONResponse:
        """Handle FastAPI HTTP exceptions"""
        
        context = ErrorContext(
            error_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            service_name=self.service_name,
            endpoint=str(request.url.path),
            request_id=request.headers.get("X-Request-ID")
        )
        
        error_response = self.create_error_response(
            status_code=exc.status_code,
            title="HTTP Error",
            detail=exc.detail,
            context=context
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response
        )
    
    async def handle_general_exception(
        self,
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """Handle general Python exceptions"""
        
        context = ErrorContext(
            error_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            service_name=self.service_name,
            endpoint=str(request.url.path),
            request_id=request.headers.get("X-Request-ID"),
            stack_trace=traceback.format_exc()
        )
        
        error_response = self.create_error_response(
            status_code=500,
            title="Internal Server Error",
            detail="An unexpected error occurred. Please contact support.",
            error_type=f"urn:{self.service_name}:error:internal",
            context=context
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response
        )

# Standard error types
VALIDATION_ERROR = "urn:opex:error:validation"
RESOURCE_NOT_FOUND = "urn:opex:error:not-found" 
AUTHENTICATION_ERROR = "urn:opex:error:authentication"
AUTHORIZATION_ERROR = "urn:opex:error:authorization"
RATE_LIMIT_ERROR = "urn:opex:error:rate-limit"
DEPENDENCY_ERROR = "urn:opex:error:dependency"
