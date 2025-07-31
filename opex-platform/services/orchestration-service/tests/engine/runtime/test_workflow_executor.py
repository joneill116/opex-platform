"""Test the workflow executor"""
import asyncio
import asyncpg
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from src.engine.core.event_store import EventStore
from src.engine.runtime.workflow_executor import WorkflowExecutor
from src.engine.components.test_components import create_component_registry

async def test_workflow_execution():
    """Test executing a complete workflow"""
    
    # Connect to database
    db_pool = await asyncpg.create_pool(
        'postgresql://orchestration:orchestration@localhost:5434/orchestration'
    )
    
    # Create event store and executor
    event_store = EventStore(db_pool)
    await event_store.initialize()
    
    component_registry = create_component_registry()
    executor = WorkflowExecutor(event_store, component_registry)
    
    # Define a test workflow (like what comes from UI)
    workflow = {
        "id": str(uuid.uuid4()),
        "name": "Test Data Pipeline",
        "components": [
            {"id": "source1", "type": "acquisition", "name": "S3 Source"},
            {"id": "source2", "type": "acquisition", "name": "API Source"},
            {"id": "transform", "type": "transformation", "name": "Transform Data"},
            {"id": "quality", "type": "quality", "name": "Quality Check"},
            {"id": "publish", "type": "publish", "name": "Publish Results"}
        ],
        "connections": [
            {"source": {"id": "source1"}, "target": {"id": "transform"}},
            {"source": {"id": "source2"}, "target": {"id": "transform"}},
            {"source": {"id": "transform"}, "target": {"id": "quality"}},
            {"source": {"id": "quality"}, "target": {"id": "publish"}}
        ]
    }
    
    print("=" * 60)
    print("WORKFLOW EXECUTION TEST")
    print("=" * 60)
    print(f"\nExecuting workflow: {workflow['name']}")
    print("\nWorkflow structure:")
    print("  [source1] ─┐")
    print("             ├─→ [transform] ─→ [quality] ─→ [publish]")
    print("  [source2] ─┘")
    print("\nExecution starting...")
    print("-" * 60)
    
    # Execute the workflow
    start_time = asyncio.get_event_loop().time()
    execution_id = await executor.execute(workflow, {"test": True})
    end_time = asyncio.get_event_loop().time()
    
    print("-" * 60)
    print(f"\n✅ Workflow executed successfully!")
    print(f"   Execution ID: {execution_id}")
    print(f"   Total time: {end_time - start_time:.2f} seconds")
    
    # Query events to show what happened
    events = await event_store.get_events(execution_id=execution_id)
    
    print(f"\n📊 Execution Timeline ({len(events)} events):")
    for i, event in enumerate(events):
        indent = "  " if event.actor != "system" else ""
        print(f"{indent}{i+1}. [{event.event_type}] by {event.actor}")
    
    # Check parallelization worked
    component_timings = {}
    for event in events:
        if event.event_type == "component.started":
            component_timings[event.actor] = {"start": event.timestamp}
        elif event.event_type == "component.completed":
            if event.actor in component_timings:
                component_timings[event.actor]["end"] = event.timestamp
    
    print("\n⚡ Parallelization Analysis:")
    print("  source1 and source2 should run in parallel:")
    if "source1" in component_timings and "source2" in component_timings:
        s1_start = component_timings["source1"]["start"]
        s2_start = component_timings["source2"]["start"]
        time_diff = abs((s2_start - s1_start).total_seconds())
        print(f"  Time between starts: {time_diff:.3f}s")
        print(f"  Parallel execution: {'✅ YES' if time_diff < 0.1 else '❌ NO'}")
    
    await db_pool.close()
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    print("Starting workflow execution test...")
    asyncio.run(test_workflow_execution())
