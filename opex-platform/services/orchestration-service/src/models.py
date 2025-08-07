from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class ComponentType(str, Enum):
    ACQUISITION = "acquisition"
    TRANSFORMATION = "transformation" 
    TECHNICAL_QUALITY = "technical-quality"
    ENRICHMENT = "enrichment"
    BUSINESS_QUALITY = "business-quality"
    PUBLISH = "publish"

class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class Component(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: ComponentType
    name: str
    config: Dict[str, Any] = {}
    position: Dict[str, float] = {"x": 0, "y": 0}  # For visual positioning
    
class Connection(BaseModel):
    source_id: str
    target_id: str

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    severity: str = "high"
    solutions: List[str] = Field(default_factory=list)
    components: Optional[List[Dict]] = Field(default_factory=list)
    connections: Optional[List[Dict]] = Field(default_factory=list)

class Workflow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    severity: str
    solutions: List[str] = []
    status: WorkflowStatus = WorkflowStatus.DRAFT
    components: List[Component] = Field(default_factory=list)
    connections: List[Connection] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "system"  # Will integrate with auth later

class WorkflowExecution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    status: str = "pending"  # pending, running, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
