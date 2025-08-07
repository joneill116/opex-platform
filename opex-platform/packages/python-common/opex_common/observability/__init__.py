"""
WORLD-CLASS OBSERVABILITY STACK
Following OpenTelemetry standards with enterprise-grade monitoring.
"""

from datetime import datetime
from typing import Any, Dict, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict
import uuid
import json
from contextlib import asynccontextmanager
import asyncio
import time

# Import centralized logging
try:
    from ..logging import get_logger
    logger = get_logger("observability")
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    from opentelemetry import trace, metrics
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False

class AlertLevel(str, Enum):
    """Alert severity levels following SRE best practices"""
    CRITICAL = "critical"    # System down, immediate response required
    ERROR = "error"          # Feature broken, affects users
    WARNING = "warning"      # Degraded performance, investigate soon
    INFO = "info"           # Normal operational messages

class MetricType(str, Enum):
    """Metric types for observability"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class Alert:
    """Structured alert for enterprise monitoring"""
    alert_id: str
    service_name: str
    level: AlertLevel
    title: str
    description: str
    timestamp: datetime
    tags: Dict[str, str]
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    runbook_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }

class MetricCollector:
    """Enterprise-grade metrics collection following Prometheus standards"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.metrics: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    def counter(self, name: str, labels: Dict[str, str] = None, help_text: str = ""):
        """Create/increment a counter metric"""
        labels = labels or {}
        key = f"{name}_{hash(str(sorted(labels.items())))}"
        
        if key not in self.metrics:
            self.metrics[key] = {
                'name': name,
                'type': MetricType.COUNTER,
                'help': help_text,
                'labels': labels,
                'value': 0,
                'last_updated': datetime.utcnow()
            }
        
        self.metrics[key]['value'] += 1
        self.metrics[key]['last_updated'] = datetime.utcnow()
        
        logger.info(
            "metric.counter.incremented",
            metric_name=name,
            labels=labels,
            value=self.metrics[key]['value']
        )
    
    def gauge(self, name: str, value: float, labels: Dict[str, str] = None, help_text: str = ""):
        """Set a gauge metric"""
        labels = labels or {}
        key = f"{name}_{hash(str(sorted(labels.items())))}"
        
        self.metrics[key] = {
            'name': name,
            'type': MetricType.GAUGE,
            'help': help_text,
            'labels': labels,
            'value': value,
            'last_updated': datetime.utcnow()
        }
        
        logger.info(
            "metric.gauge.set",
            metric_name=name,
            labels=labels,
            value=value
        )
    
    def histogram(self, name: str, value: float, labels: Dict[str, str] = None, help_text: str = ""):
        """Record a histogram measurement"""
        labels = labels or {}
        key = f"{name}_{hash(str(sorted(labels.items())))}"
        
        if key not in self.metrics:
            self.metrics[key] = {
                'name': name,
                'type': MetricType.HISTOGRAM,
                'help': help_text,
                'labels': labels,
                'values': [],
                'count': 0,
                'sum': 0.0,
                'last_updated': datetime.utcnow()
            }
        
        self.metrics[key]['values'].append(value)
        self.metrics[key]['count'] += 1
        self.metrics[key]['sum'] += value
        self.metrics[key]['last_updated'] = datetime.utcnow()
        
        logger.info(
            "metric.histogram.recorded",
            metric_name=name,
            labels=labels,
            value=value
        )

class AlertManager:
    """Enterprise alert management with SRE principles"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.alerts: List[Alert] = []
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        
    def register_alert_rule(self, rule_name: str, condition: str, level: AlertLevel, 
                          description: str, threshold: float = None, runbook_url: str = None):
        """Register an alert rule"""
        self.alert_rules[rule_name] = {
            'condition': condition,
            'level': level,
            'description': description,
            'threshold': threshold,
            'runbook_url': runbook_url
        }
        
        logger.info(
            "alert.rule.registered",
            rule_name=rule_name,
            level=level.value,
            condition=condition
        )
    
    def fire_alert(self, rule_name: str, metric_value: float = None, 
                   tags: Dict[str, str] = None) -> Alert:
        """Fire an alert based on a rule"""
        if rule_name not in self.alert_rules:
            raise ValueError(f"Alert rule '{rule_name}' not found")
        
        rule = self.alert_rules[rule_name]
        alert = Alert(
            alert_id=str(uuid.uuid4()),
            service_name=self.service_name,
            level=rule['level'],
            title=f"Alert: {rule_name}",
            description=rule['description'],
            timestamp=datetime.utcnow(),
            tags=tags or {},
            metric_value=metric_value,
            threshold=rule.get('threshold'),
            runbook_url=rule.get('runbook_url')
        )
        
        self.alerts.append(alert)
        
        # Log alert with appropriate level
        log_func = getattr(logger, alert.level.value)
        log_func(
            f"ALERT.{alert.level.value.upper()}",
            alert_id=alert.alert_id,
            service=self.service_name,
            rule_name=rule_name,
            description=alert.description,
            metric_value=metric_value,
            threshold=rule.get('threshold'),
            tags=tags
        )
        
        return alert

class DistributedTracer:
    """World-class distributed tracing with OpenTelemetry"""
    
    def __init__(self, service_name: str, jaeger_endpoint: str = None):
        self.service_name = service_name
        
        if TELEMETRY_AVAILABLE and jaeger_endpoint:
            self._setup_jaeger_tracing(jaeger_endpoint)
            self.tracer = trace.get_tracer(__name__)
        else:
            self.tracer = None
    
    def _setup_jaeger_tracing(self, jaeger_endpoint: str):
        """Configure Jaeger distributed tracing"""
        resource = Resource(attributes={
            SERVICE_NAME: self.service_name
        })
        
        trace.set_tracer_provider(TracerProvider(resource=resource))
        
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_endpoint.split('://')[1].split(':')[0],
            agent_port=int(jaeger_endpoint.split(':')[-1]),
        )
        
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        logger.info(
            "distributed.tracing.initialized",
            service=self.service_name,
            jaeger_endpoint=jaeger_endpoint
        )
    
    @asynccontextmanager
    async def span(self, operation_name: str, tags: Dict[str, Any] = None):
        """Create a traced span"""
        if self.tracer:
            with self.tracer.start_as_current_span(operation_name) as span:
                if tags:
                    for key, value in tags.items():
                        span.set_attribute(key, str(value))
                yield span
        else:
            # Fallback for when tracing is not available
            start_time = time.time()
            try:
                yield None
            finally:
                duration = time.time() - start_time
                logger.info(
                    "operation.completed",
                    operation=operation_name,
                    duration_ms=round(duration * 1000, 2),
                    tags=tags
                )

class ObservabilityStack:
    """Complete observability solution combining metrics, logging, tracing, and alerts"""
    
    def __init__(self, service_name: str, jaeger_endpoint: str = None):
        self.service_name = service_name
        self.metrics = MetricCollector(service_name)
        self.alerts = AlertManager(service_name)
        self.tracer = DistributedTracer(service_name, jaeger_endpoint)
        
        # Register default SRE alert rules
        self._register_default_alerts()
        
        logger.info(
            "observability.stack.initialized",
            service=service_name,
            components=['metrics', 'alerts', 'tracing', 'logging']
        )
    
    def _register_default_alerts(self):
        """Register standard SRE alert rules"""
        self.alerts.register_alert_rule(
            "high_error_rate",
            "error_rate > 5%",
            AlertLevel.CRITICAL,
            "Error rate exceeded 5% threshold",
            threshold=0.05,
            runbook_url="https://docs.company.com/runbooks/high-error-rate"
        )
        
        self.alerts.register_alert_rule(
            "high_response_time",
            "p95_response_time > 1000ms",
            AlertLevel.WARNING,
            "95th percentile response time exceeded 1 second",
            threshold=1000.0,
            runbook_url="https://docs.company.com/runbooks/high-latency"
        )
        
        self.alerts.register_alert_rule(
            "service_down",
            "health_check_failed",
            AlertLevel.CRITICAL,
            "Service health check failed",
            runbook_url="https://docs.company.com/runbooks/service-down"
        )
    
    async def record_request(self, method: str, endpoint: str, status_code: int, 
                           duration_ms: float, user_id: str = None):
        """Record HTTP request metrics with full observability"""
        labels = {
            'method': method,
            'endpoint': endpoint,
            'status_code': str(status_code)
        }
        
        # Increment request counter
        self.metrics.counter('http_requests_total', labels, 'Total HTTP requests')
        
        # Record response time
        self.metrics.histogram('http_request_duration_ms', duration_ms, labels, 'HTTP request duration in milliseconds')
        
        # Track error rate
        if status_code >= 400:
            self.metrics.counter('http_requests_errors_total', labels, 'Total HTTP error requests')
            
            # Fire alert if error rate is high
            if status_code >= 500:
                self.alerts.fire_alert(
                    "high_error_rate",
                    tags={'endpoint': endpoint, 'method': method}
                )
        
        # Log the request
        logger.info(
            "http.request.completed",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            duration_ms=duration_ms,
            user_id=user_id
        )
    
    async def record_database_operation(self, operation: str, table: str, 
                                      duration_ms: float, success: bool = True):
        """Record database operation metrics"""
        labels = {
            'operation': operation,
            'table': table,
            'status': 'success' if success else 'error'
        }
        
        self.metrics.counter('database_operations_total', labels, 'Total database operations')
        self.metrics.histogram('database_operation_duration_ms', duration_ms, labels, 'Database operation duration')
        
        if not success:
            self.metrics.counter('database_errors_total', labels, 'Total database errors')
        
        logger.info(
            "database.operation.completed",
            operation=operation,
            table=table,
            duration_ms=duration_ms,
            success=success
        )
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get health metrics for monitoring"""
        return {
            'service': self.service_name,
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'metrics_count': len(self.metrics.metrics),
            'active_alerts': len([a for a in self.alerts.alerts if a.level == AlertLevel.CRITICAL]),
            'uptime_seconds': time.time() - getattr(self, '_start_time', time.time())
        }

# Global observability instance
_observability_stack: Optional[ObservabilityStack] = None

def get_observability() -> ObservabilityStack:
    """Get the global observability stack"""
    global _observability_stack
    if _observability_stack is None:
        raise RuntimeError("Observability stack not initialized. Call initialize_observability() first.")
    return _observability_stack

def initialize_observability(service_name: str, jaeger_endpoint: str = None) -> ObservabilityStack:
    """Initialize the global observability stack"""
    global _observability_stack
    _observability_stack = ObservabilityStack(service_name, jaeger_endpoint)
    _observability_stack._start_time = time.time()
    return _observability_stack
