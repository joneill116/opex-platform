"""
WORLD-CLASS EXCEPTION MANAGEMENT & RESILIENCE PATTERNS
Implementing Circuit Breakers, Bulkhead, Timeout, Retry, and Fallback patterns.
Following Netflix's Hystrix and Martin Fowler's resilience principles.
"""

import asyncio
import time
import random
from typing import Any, Dict, Optional, Callable, List, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import functools
import traceback
from contextlib import asynccontextmanager

# Import centralized logging
try:
    from ..logging import get_logger
    logger = get_logger("resilience")
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class CircuitBreakerState(str, Enum):
    """Circuit breaker states following Fowler's pattern"""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"           # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class RetryStrategy(str, Enum):
    """Retry strategies for resilience"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    JITTER = "jitter"

@dataclass
class ExceptionMetadata:
    """Rich exception context for enterprise debugging"""
    exception_id: str
    service_name: str
    operation_name: str
    timestamp: datetime
    exception_type: str
    message: str
    stack_trace: str
    context: Dict[str, Any]
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    retry_count: int = 0
    circuit_breaker_state: Optional[CircuitBreakerState] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'exception_id': self.exception_id,
            'service_name': self.service_name,
            'operation_name': self.operation_name,
            'timestamp': self.timestamp.isoformat(),
            'exception_type': self.exception_type,
            'message': self.message,
            'stack_trace': self.stack_trace,
            'context': self.context,
            'user_id': self.user_id,
            'request_id': self.request_id,
            'retry_count': self.retry_count,
            'circuit_breaker_state': self.circuit_breaker_state.value if self.circuit_breaker_state else None
        }

class CircuitBreakerException(Exception):
    """Exception raised when circuit breaker is open"""
    def __init__(self, service_name: str, operation_name: str):
        self.service_name = service_name
        self.operation_name = operation_name
        super().__init__(f"Circuit breaker OPEN for {service_name}.{operation_name}")

class TimeoutException(Exception):
    """Exception raised on timeout"""
    def __init__(self, operation_name: str, timeout_seconds: float):
        self.operation_name = operation_name
        self.timeout_seconds = timeout_seconds
        super().__init__(f"Operation {operation_name} timed out after {timeout_seconds}s")

class BulkheadFullException(Exception):
    """Exception raised when bulkhead capacity is exceeded"""
    def __init__(self, bulkhead_name: str):
        self.bulkhead_name = bulkhead_name
        super().__init__(f"Bulkhead {bulkhead_name} is at full capacity")

class CircuitBreaker:
    """
    Enterprise-grade circuit breaker implementing Fowler's pattern.
    Prevents cascading failures across microservices.
    """
    
    def __init__(self, name: str, failure_threshold: int = 5, 
                 recovery_timeout: float = 60.0, expected_exception: type = Exception):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self._lock = asyncio.Lock()
        
        logger.info(
            "circuit_breaker.initialized",
            name=name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        async with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info("circuit_breaker.half_open", name=self.name)
                else:
                    logger.warning("circuit_breaker.rejected", name=self.name)
                    raise CircuitBreakerException(self.name, func.__name__)
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            await self._on_success()
            return result
            
        except self.expected_exception as e:
            await self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset"""
        return (
            self.last_failure_time and 
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    async def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitBreakerState.HALF_OPEN:
            async with self._lock:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                logger.info("circuit_breaker.closed", name=self.name)
    
    async def _on_failure(self):
        """Handle failed call"""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                logger.error(
                    "circuit_breaker.opened",
                    name=self.name,
                    failure_count=self.failure_count
                )

class Bulkhead:
    """
    Bulkhead pattern for isolating critical resources.
    Prevents one failing component from consuming all resources.
    """
    
    def __init__(self, name: str, max_concurrent_requests: int = 10):
        self.name = name
        self.max_concurrent_requests = max_concurrent_requests
        self.current_requests = 0
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        
        logger.info(
            "bulkhead.initialized",
            name=name,
            max_concurrent_requests=max_concurrent_requests
        )
    
    @asynccontextmanager
    async def acquire(self):
        """Acquire bulkhead slot"""
        if self.current_requests >= self.max_concurrent_requests:
            logger.warning("bulkhead.capacity_exceeded", name=self.name)
            raise BulkheadFullException(self.name)
        
        async with self._semaphore:
            self.current_requests += 1
            try:
                logger.debug(
                    "bulkhead.acquired",
                    name=self.name,
                    current_requests=self.current_requests
                )
                yield
            finally:
                self.current_requests -= 1
                logger.debug(
                    "bulkhead.released",
                    name=self.name,
                    current_requests=self.current_requests
                )

class RetryManager:
    """
    Sophisticated retry mechanism with multiple strategies.
    Implements exponential backoff with jitter to prevent thundering herd.
    """
    
    def __init__(self, max_retries: int = 3, strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
                 base_delay: float = 1.0, max_delay: float = 60.0, jitter: bool = True):
        self.max_retries = max_retries
        self.strategy = strategy
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
    
    async def execute(self, func: Callable, *args, **kwargs):
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
                    
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    
                    logger.warning(
                        "retry.attempt_failed",
                        function=func.__name__,
                        attempt=attempt + 1,
                        max_retries=self.max_retries,
                        delay_seconds=delay,
                        error=str(e)
                    )
                    
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        "retry.exhausted",
                        function=func.__name__,
                        attempts=attempt + 1,
                        final_error=str(e)
                    )
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay based on retry strategy"""
        if self.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.base_delay * (2 ** attempt)
        elif self.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.base_delay * (attempt + 1)
        else:  # FIXED_DELAY
            delay = self.base_delay
        
        # Apply max delay limit
        delay = min(delay, self.max_delay)
        
        # Add jitter to prevent thundering herd
        if self.jitter:
            delay *= (0.5 + random.random() * 0.5)
        
        return delay

class TimeoutManager:
    """Timeout management with proper cancellation"""
    
    @staticmethod
    async def with_timeout(coro, timeout_seconds: float, operation_name: str = None):
        """Execute coroutine with timeout"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout_seconds)
        except asyncio.TimeoutError:
            operation = operation_name or getattr(coro, '__name__', 'unknown_operation')
            logger.error(
                "timeout.exceeded",
                operation=operation,
                timeout_seconds=timeout_seconds
            )
            raise TimeoutException(operation, timeout_seconds)

class FallbackManager:
    """Fallback patterns for graceful degradation"""
    
    @staticmethod
    async def with_fallback(primary_func: Callable, fallback_func: Callable, 
                          *args, **kwargs):
        """Execute primary function with fallback"""
        try:
            if asyncio.iscoroutinefunction(primary_func):
                return await primary_func(*args, **kwargs)
            else:
                return primary_func(*args, **kwargs)
                
        except Exception as e:
            logger.warning(
                "fallback.triggered",
                primary_function=primary_func.__name__,
                fallback_function=fallback_func.__name__,
                error=str(e)
            )
            
            try:
                if asyncio.iscoroutinefunction(fallback_func):
                    return await fallback_func(*args, **kwargs)
                else:
                    return fallback_func(*args, **kwargs)
            except Exception as fallback_error:
                logger.error(
                    "fallback.failed",
                    fallback_function=fallback_func.__name__,
                    error=str(fallback_error)
                )
                raise

class ResilienceOrchestrator:
    """
    Master orchestrator combining all resilience patterns.
    This is the enterprise-grade solution for microservices resilience.
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.bulkheads: Dict[str, Bulkhead] = {}
        self._exception_history: List[ExceptionMetadata] = []
        
        logger.info("resilience.orchestrator.initialized", service=service_name)
    
    def get_circuit_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """Get or create circuit breaker"""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name, **kwargs)
        return self.circuit_breakers[name]
    
    def get_bulkhead(self, name: str, **kwargs) -> Bulkhead:
        """Get or create bulkhead"""
        if name not in self.bulkheads:
            self.bulkheads[name] = Bulkhead(name, **kwargs)
        return self.bulkheads[name]
    
    async def execute_with_resilience(
        self,
        func: Callable,
        operation_name: str,
        circuit_breaker_config: Dict[str, Any] = None,
        bulkhead_config: Dict[str, Any] = None,
        retry_config: Dict[str, Any] = None,
        timeout_seconds: float = None,
        fallback_func: Callable = None,
        context: Dict[str, Any] = None,
        *args,
        **kwargs
    ):
        """
        Execute function with full resilience patterns:
        - Circuit Breaker: Prevent cascading failures
        - Bulkhead: Isolate resources
        - Retry: Handle transient failures
        - Timeout: Prevent hanging requests
        - Fallback: Graceful degradation
        """
        start_time = time.time()
        exception_context = context or {}
        
        try:
            # Get circuit breaker if configured
            circuit_breaker = None
            if circuit_breaker_config:
                circuit_breaker = self.get_circuit_breaker(
                    f"{operation_name}_cb", 
                    **circuit_breaker_config
                )
            
            # Get bulkhead if configured
            bulkhead = None
            if bulkhead_config:
                bulkhead = self.get_bulkhead(
                    f"{operation_name}_bulkhead",
                    **bulkhead_config
                )
            
            # Prepare retry manager if configured
            retry_manager = RetryManager(**retry_config) if retry_config else None
            
            async def protected_execution():
                """Inner function with all protections"""
                # Apply bulkhead protection
                if bulkhead:
                    async with bulkhead.acquire():
                        return await self._execute_core(
                            func, circuit_breaker, retry_manager, 
                            timeout_seconds, operation_name, *args, **kwargs
                        )
                else:
                    return await self._execute_core(
                        func, circuit_breaker, retry_manager,
                        timeout_seconds, operation_name, *args, **kwargs
                    )
            
            # Apply fallback if configured
            if fallback_func:
                return await FallbackManager.with_fallback(
                    protected_execution, fallback_func, *args, **kwargs
                )
            else:
                return await protected_execution()
                
        except Exception as e:
            # Record exception with full context
            await self._record_exception(
                e, operation_name, exception_context, 
                circuit_breaker.state if circuit_breaker else None
            )
            raise
        finally:
            # Record execution metrics
            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                "resilience.execution.completed",
                service=self.service_name,
                operation=operation_name,
                duration_ms=duration_ms
            )
    
    async def _execute_core(self, func: Callable, circuit_breaker: CircuitBreaker = None,
                          retry_manager: RetryManager = None, timeout_seconds: float = None,
                          operation_name: str = None, *args, **kwargs):
        """Core execution with circuit breaker, retry, and timeout"""
        
        async def execute_func():
            if circuit_breaker:
                return await circuit_breaker.call(func, *args, **kwargs)
            else:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
        
        # Apply retry logic
        if retry_manager:
            execution_func = lambda: retry_manager.execute(execute_func)
        else:
            execution_func = execute_func
        
        # Apply timeout
        if timeout_seconds:
            return await TimeoutManager.with_timeout(
                execution_func(), timeout_seconds, operation_name
            )
        else:
            return await execution_func()
    
    async def _record_exception(self, exception: Exception, operation_name: str,
                              context: Dict[str, Any], circuit_breaker_state: CircuitBreakerState = None):
        """Record exception with full metadata"""
        import uuid
        
        exception_metadata = ExceptionMetadata(
            exception_id=str(uuid.uuid4()),
            service_name=self.service_name,
            operation_name=operation_name,
            timestamp=datetime.utcnow(),
            exception_type=type(exception).__name__,
            message=str(exception),
            stack_trace=traceback.format_exc(),
            context=context,
            circuit_breaker_state=circuit_breaker_state
        )
        
        self._exception_history.append(exception_metadata)
        
        # Keep only last 1000 exceptions to prevent memory issues
        if len(self._exception_history) > 1000:
            self._exception_history = self._exception_history[-1000:]
        
        logger.error(
            "exception.recorded",
            **exception_metadata.to_dict()
        )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status including resilience metrics"""
        circuit_breaker_status = {
            name: {
                'state': cb.state.value,
                'failure_count': cb.failure_count,
                'last_failure_time': cb.last_failure_time
            }
            for name, cb in self.circuit_breakers.items()
        }
        
        bulkhead_status = {
            name: {
                'current_requests': bh.current_requests,
                'max_concurrent_requests': bh.max_concurrent_requests,
                'utilization_percent': (bh.current_requests / bh.max_concurrent_requests) * 100
            }
            for name, bh in self.bulkheads.items()
        }
        
        return {
            'service': self.service_name,
            'circuit_breakers': circuit_breaker_status,
            'bulkheads': bulkhead_status,
            'recent_exceptions': len([
                e for e in self._exception_history 
                if (datetime.utcnow() - e.timestamp).total_seconds() < 300  # Last 5 minutes
            ]),
            'total_exceptions': len(self._exception_history)
        }

# Decorator for easy resilience application
def resilient(
    circuit_breaker: Dict[str, Any] = None,
    bulkhead: Dict[str, Any] = None,
    retry: Dict[str, Any] = None,
    timeout: float = None,
    fallback: Callable = None
):
    """Decorator to apply resilience patterns to functions"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get or create orchestrator (this would be injected in real implementation)
            orchestrator = ResilienceOrchestrator(func.__module__.split('.')[0])
            
            return await orchestrator.execute_with_resilience(
                func=func,
                operation_name=func.__name__,
                circuit_breaker_config=circuit_breaker,
                bulkhead_config=bulkhead,
                retry_config=retry,
                timeout_seconds=timeout,
                fallback_func=fallback,
                *args,
                **kwargs
            )
        return wrapper
    return decorator
