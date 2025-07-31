from enum import Enum
from typing import Optional, Dict, Any
import hashlib
import json

class WorkflowState(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ComponentState(Enum):
    PENDING = "pending"
    READY = "ready"  # Dependencies satisfied
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class DeterministicStateMachine:
    """
    Ensures workflow execution is completely deterministic.
    Same events → Same state, always.
    """
    
    def __init__(self, workflow_id: str, execution_id: str):
        self.workflow_id = workflow_id
        self.execution_id = execution_id
        self.workflow_state = WorkflowState.PENDING
        self.component_states: Dict[str, ComponentState] = {}
        self.execution_hash = self._init_hash()
        
    def _init_hash(self) -> str:
        """Initialize deterministic hash"""
        return hashlib.sha256(
            f"{self.workflow_id}:{self.execution_id}".encode()
        ).hexdigest()
    
    def transition(self, event: WorkflowEvent) -> Dict[str, Any]:
        """
        Apply event to state machine.
        Returns new state and side effects.
        """
        # Update hash for determinism verification
        self.execution_hash = self._update_hash(self.execution_hash, event)
        
        # State transitions based on event type
        if event.event_type == "workflow.started":
            return self._handle_workflow_started(event)
        elif event.event_type == "component.ready":
            return self._handle_component_ready(event)
        elif event.event_type == "component.started":
            return self._handle_component_started(event)
        elif event.event_type == "component.completed":
            return self._handle_component_completed(event)
        elif event.event_type == "component.failed":
            return self._handle_component_failed(event)
        
    def _handle_component_completed(self, event: WorkflowEvent) -> Dict[str, Any]:
        """Handle component completion - determine what can run next"""
        component_id = event.data['component_id']
        self.component_states[component_id] = ComponentState.COMPLETED
        
        # Check which components are now ready
        newly_ready = self._check_ready_components()
        
        return {
            'state_changes': {
                component_id: ComponentState.COMPLETED
            },
            'ready_components': newly_ready,
            'workflow_progress': self._calculate_progress()
        }
