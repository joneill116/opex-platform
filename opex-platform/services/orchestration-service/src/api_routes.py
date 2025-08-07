from fastapi import APIRouter, Request, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
import uuid
from .models import Workflow, WorkflowCreate, Component, Connection, ComponentType, WorkflowStatus
from .repositories import WorkflowRepository, get_workflow_repository

router = APIRouter()


@router.get("/workflows", response_model=List[Workflow])
async def list_workflows(
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    repository: WorkflowRepository = Depends(get_workflow_repository)
):
    """List all workflows with optional filtering"""
    status_enum = None
    if status:
        try:
            status_enum = WorkflowStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    workflows = await repository.list_workflows(status=status_enum)
    return workflows[skip : skip + limit]

@router.post("/workflows", response_model=Workflow)
async def create_workflow(
    workflow_data: WorkflowCreate,
    repository: WorkflowRepository = Depends(get_workflow_repository)
):
    """Create a new workflow"""
    return await repository.create_workflow(workflow_data)

@router.get("/workflows/{workflow_id}", response_model=Workflow)
async def get_workflow(
    workflow_id: str,
    repository: WorkflowRepository = Depends(get_workflow_repository)
):
    """Get a specific workflow by ID"""
    workflow = await repository.get_workflow_by_id(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.put("/workflows/{workflow_id}", response_model=Workflow)
async def update_workflow(
    workflow_id: str,
    workflow_data: WorkflowCreate,
    repository: WorkflowRepository = Depends(get_workflow_repository)
):
    """Update an existing workflow"""
    update_data = workflow_data.dict(exclude_unset=True)
    workflow = await repository.update_workflow(workflow_id, update_data)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.delete("/workflows/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    repository: WorkflowRepository = Depends(get_workflow_repository)
):
    """Delete a workflow (soft delete - archives it)"""
    success = await repository.delete_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"message": "Workflow archived successfully"}

@router.post("/workflows/{workflow_id}/components", response_model=Workflow)
async def add_component(
    workflow_id: str,
    component: Component,
    repository: WorkflowRepository = Depends(get_workflow_repository)
):
    """Add a component to a workflow"""
    workflow = await repository.get_workflow_by_id(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Add component to workflow
    workflow.components.append(component)
    updated_workflow = await repository.update_workflow(workflow_id, {
        "components": [comp.dict() for comp in workflow.components]
    })
    return updated_workflow

@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    request: Request,
    repository: WorkflowRepository = Depends(get_workflow_repository)
):
    """Execute a workflow"""
    workflow = await repository.get_workflow_by_id(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Convert to the format the executor expects
    workflow_data = {
        "id": workflow.id,
        "name": workflow.name,
        "components": [comp.dict() for comp in workflow.components],
        "connections": [conn.dict() for conn in workflow.connections]
    }
    
    # Get executor from app state
    executor = request.app.state.workflow_executor
    
    # Execute workflow
    execution_id = await executor.execute(workflow_data)
    
    return {
        "execution_id": execution_id,
        "status": "started",
        "workflow_id": workflow_id
    }

@router.get("/components/types")
async def get_component_types():
    """Get available component types and their configurations"""
    return {
        "types": [
            {
                "type": ComponentType.ACQUISITION,
                "name": "Data Acquisition",
                "description": "Collect data from various sources",
                "icon": "database",
                "color": "#3B82F6"
            },
            {
                "type": ComponentType.TRANSFORMATION,
                "name": "Transformation",
                "description": "Transform and reshape data",
                "icon": "shuffle",
                "color": "#8B5CF6"
            },
            {
                "type": ComponentType.TECHNICAL_QUALITY,
                "name": "Technical Quality",
                "description": "Validate data quality",
                "icon": "check-circle",
                "color": "#10B981"
            },
            {
                "type": ComponentType.BUSINESS_QUALITY,
                "name": "Business Quality",
                "description": "Apply business rules",
                "icon": "briefcase",
                "color": "#F59E0B"
            },
            {
                "type": ComponentType.ENRICHMENT,
                "name": "Enrichment",
                "description": "Enhance data with additional information",
                "icon": "plus-circle",
                "color": "#6366F1"
            },
            {
                "type": ComponentType.PUBLISH,
                "name": "Publish",
                "description": "Send data to destinations",
                "icon": "upload",
                "color": "#EF4444"
            }
        ]
    }

@router.get("/executions/{execution_id}")
async def get_execution_status(execution_id: str, request: Request):
    """Get execution status and events"""
    event_store = request.app.state.event_store
    
    # Validate UUID format
    try:
        uuid.UUID(execution_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid execution ID format")
    
    # Get all events for this execution
    events = await event_store.get_events(execution_id=execution_id)
    
    if not events:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Determine status
    status = "running"
    for event in events:
        if event.event_type == "workflow.completed":
            status = "completed"
        elif event.event_type == "workflow.failed":
            status = "failed"
    
    return {
        "execution_id": execution_id,
        "status": status,
        "event_count": len(events),
        "events": [
            {
                "event_type": event.event_type,
                "actor": event.actor,
                "timestamp": event.timestamp.isoformat()
            }
            for event in events[-10:]  # Last 10 events
        ]
    }
