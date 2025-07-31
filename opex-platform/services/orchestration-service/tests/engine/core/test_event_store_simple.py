import asyncio
import asyncpg
import json
import uuid
from datetime import datetime, timezone
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from src.engine.core.event_store import EventStore, WorkflowEvent

async def test_event_store_connection():
    """Test basic database connection and table creation"""
    db_pool = await asyncpg.create_pool(
        'postgresql://orchestration:orchestration@localhost:5434/orchestration'
    )
    
    print("Testing Event Store Connection...")
    
    # Verify tables exist
    async with db_pool.acquire() as conn:
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'workflow_events'
            )
        """)
        assert result, "workflow_events table should exist"
        print("✓ workflow_events table exists")
        
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'execution_snapshots'
            )
        """)
        assert result, "execution_snapshots table should exist"
        print("✓ execution_snapshots table exists")
    
    await db_pool.close()
    print("✓ Database connection test passed!")

async def test_event_append_and_retrieve():
    """Test appending and retrieving events"""
    db_pool = await asyncpg.create_pool(
        'postgresql://orchestration:orchestration@localhost:5434/orchestration'
    )
    
    print("\nTesting Event Append and Retrieve...")
    
    # Create event store
    event_store = EventStore(db_pool)
    
    # Create test workflow and execution
    workflow_id = str(uuid.uuid4())
    execution_id = str(uuid.uuid4())
    
    # Test event 1: Workflow started
    event1 = WorkflowEvent(
        workflow_id=workflow_id,
        execution_id=execution_id,
        event_type="workflow.started",
        actor="system",
        data={"components": 3, "user": "test-user"}
    )
    
    seq1 = await event_store.append(event1)
    print(f"✓ Appended workflow.started (sequence: {seq1})")
    
    # Test event 2: Component started
    event2 = WorkflowEvent(
        workflow_id=workflow_id,
        execution_id=execution_id,
        event_type="component.started",
        actor="acquisition-1",
        data={"type": "s3", "bucket": "test-bucket"}
    )
    
    seq2 = await event_store.append(event2)
    print(f"✓ Appended component.started (sequence: {seq2})")
    assert seq2 > seq1, "Sequence numbers should increment"
    
    # Retrieve events
    events = await event_store.get_events(execution_id=execution_id)
    assert len(events) == 2, f"Should have 2 events, got {len(events)}"
    print(f"✓ Retrieved {len(events)} events")
    
    # Verify event order
    assert events[0].event_type == "workflow.started"
    assert events[1].event_type == "component.started"
    print("✓ Events in correct order")
    
    await db_pool.close()
    print("✓ Event append/retrieve test passed!")

async def test_event_filtering():
    """Test event filtering capabilities"""
    db_pool = await asyncpg.create_pool(
        'postgresql://orchestration:orchestration@localhost:5434/orchestration'
    )
    
    print("\nTesting Event Filtering...")
    
    event_store = EventStore(db_pool)
    
    # Create multiple workflows
    workflow1_id = str(uuid.uuid4())
    workflow2_id = str(uuid.uuid4())
    execution1_id = str(uuid.uuid4())
    execution2_id = str(uuid.uuid4())
    
    # Add events for workflow 1
    await event_store.append(WorkflowEvent(
        workflow_id=workflow1_id,
        execution_id=execution1_id,
        event_type="workflow.started",
        actor="system",
        data={}
    ))
    
    await event_store.append(WorkflowEvent(
        workflow_id=workflow1_id,
        execution_id=execution1_id,
        event_type="component.started",
        actor="comp-1",
        data={}
    ))
    
    # Add events for workflow 2
    await event_store.append(WorkflowEvent(
        workflow_id=workflow2_id,
        execution_id=execution2_id,
        event_type="workflow.started",
        actor="system",
        data={}
    ))
    
    # Test filtering by workflow
    events = await event_store.get_events(workflow_id=workflow1_id)
    assert len(events) == 2, "Should have 2 events for workflow 1"
    print("✓ Filter by workflow_id works")
    
    # Test filtering by event type
    events = await event_store.get_events(event_types=["workflow.started"])
    assert len(events) >= 2, "Should have at least 2 workflow.started events"
    assert all(e.event_type == "workflow.started" for e in events)
    print("✓ Filter by event_type works")
    
    await db_pool.close()
    print("✓ Event filtering test passed!")

async def run_all_tests():
    """Run all event store tests"""
    print("=" * 50)
    print("Running Event Store Tests")
    print("=" * 50)
    
    try:
        await test_event_store_connection()
        await test_event_append_and_retrieve()
        await test_event_filtering()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
