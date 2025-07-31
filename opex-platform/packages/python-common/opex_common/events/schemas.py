# packages/python-common/opex_common/events/schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class EventType(str, Enum):
    # Workflow events
    WORKFLOW_CREATED = "workflow.created"
    WORKFLOW_UPDATED = "workflow.updated"
    WORKFLOW_DELETED = "workflow.deleted"
    WORKFLOW_DEPLOYED = "workflow.deployed"
    
    # Execution events
    EXECUTION_STARTED = "execution.started"
    EXECUTION_COMPLETED = "execution.completed"
    EXECUTION_FAILED = "execution.failed"
    COMPONENT_STARTED = "component.started"
    COMPONENT_COMPLETED = "component.completed"
    COMPONENT_FAILED = "component.failed"
    
    # Exception events
    EXCEPTION_CREATED = "exception.created"
    EXCEPTION_ASSIGNED = "exception.assigned"
    EXCEPTION_RESOLVED = "exception.resolved"
    SLA_BREACHED = "sla.breached"

class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    service_name: str
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class WorkflowEvent(BaseEvent):
    workflow_id: str
    workflow_name: str
    version: str
    user_id: str

class ExecutionEvent(BaseEvent):
    execution_id: str
    workflow_id: str
    component_id: Optional[str] = None
    status: str
    details: Dict[str, Any] = Field(default_factory=dict)
