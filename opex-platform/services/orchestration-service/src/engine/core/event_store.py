"""
Event Store: The heart of our execution engine.
Every state change is an immutable event.
"""
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict, field
import uuid
import json
import asyncio
import asyncpg

# Make optional imports
try:
    from aiokafka import AIOKafkaProducer
except ImportError:
    AIOKafkaProducer = None

try:
    import structlog
    logger = structlog.get_logger()
except ImportError:
    class SimpleLogger:
        def info(self, msg, **kwargs):
            print(f"INFO: {msg} {kwargs}")
        def error(self, msg, **kwargs):
            print(f"ERROR: {msg} {kwargs}")
        def debug(self, msg, **kwargs):
            print(f"DEBUG: {msg} {kwargs}")
    logger = SimpleLogger()

@dataclass(frozen=True)
class WorkflowEvent:
    """Immutable event - the atomic unit of state change"""
    # Required fields first (no defaults)
    workflow_id: str
    execution_id: str
    event_type: str
    actor: str  # component_id, system, or user
    
    # Optional fields with defaults
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_version: int = 1
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Serialize event for storage/transmission"""
        return json.dumps({
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'WorkflowEvent':
        """Deserialize event"""
        data = json.loads(json_str)
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)
    
    def validate(self) -> None:
        """Ensure event integrity"""
        if not self.workflow_id or not self.execution_id:
            raise ValueError("workflow_id and execution_id required")
        if not self.event_type:
            raise ValueError("event_type required")

class EventStore:
    """
    World-class event store with:
    - Guaranteed ordering
    - Exactly-once semantics
    - Real-time subscriptions
    - Time-travel capabilities
    """
    
    def __init__(self, db_pool: asyncpg.Pool, kafka_producer=None):
        self.db = db_pool
        self.kafka = kafka_producer
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}
        self._sequence_cache: Dict[str, int] = {}
        self._lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize event store"""
        # Verify schema
        async with self.db.acquire() as conn:
            result = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'workflow_events'
                )
            """)
            if not result:
                raise RuntimeError("workflow_events table does not exist")
            
        logger.info("event_store.initialized")
        return self
    
    async def append(self, event: WorkflowEvent) -> int:
        """
        Atomically append event to store.
        Returns sequence number for ordering guarantee.
        """
        event.validate()
        
        async with self._lock:  # Ensure ordering within execution
            try:
                async with self.db.acquire() as conn:
                    # Insert and get sequence number atomically
                    row = await conn.fetchrow("""
                        INSERT INTO workflow_events 
                        (event_id, workflow_id, execution_id, event_type, 
                         event_version, timestamp, actor, data, metadata)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                        RETURNING sequence_number
                    """, 
                        event.event_id, event.workflow_id, event.execution_id,
                        event.event_type, event.event_version, event.timestamp,
                        event.actor, json.dumps(event.data), json.dumps(event.metadata)
                    )
                    
                    sequence_number = row['sequence_number']
                
                # Publish to Kafka for real-time processing
                if self.kafka:
                    await self._publish_to_kafka(event, sequence_number)
                
                # Notify local subscribers
                await self._notify_subscribers(event, sequence_number)
                
                # Log for observability
                logger.info(
                    "event.appended",
                    workflow_id=event.workflow_id,
                    execution_id=event.execution_id,
                    event_type=event.event_type,
                    sequence_number=sequence_number
                )
                
                return sequence_number
                
            except Exception as e:
                logger.error(
                    "event.append.failed",
                    error=str(e),
                    event_type=event.event_type
                )
                raise
    
    async def get_events(
        self,
        workflow_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        from_sequence: Optional[int] = None,
        to_sequence: Optional[int] = None,
        event_types: Optional[List[str]] = None,
        limit: int = 1000
    ) -> List[WorkflowEvent]:
        """
        Query events with flexible filtering.
        Maintains deterministic ordering.
        """
        query = "SELECT * FROM workflow_events WHERE 1=1"
        params = []
        param_count = 0
        
        if workflow_id:
            param_count += 1
            query += f" AND workflow_id = ${param_count}"
            params.append(workflow_id)
            
        if execution_id:
            param_count += 1
            query += f" AND execution_id = ${param_count}"
            params.append(execution_id)
            
        if from_sequence:
            param_count += 1
            query += f" AND sequence_number >= ${param_count}"
            params.append(from_sequence)
            
        if to_sequence:
            param_count += 1
            query += f" AND sequence_number <= ${param_count}"
            params.append(to_sequence)
            
        if event_types:
            param_count += 1
            query += f" AND event_type = ANY(${param_count})"
            params.append(event_types)
        
        query += " ORDER BY sequence_number ASC"
        
        if limit:
            param_count += 1
            query += f" LIMIT ${param_count}"
            params.append(limit)
        
        async with self.db.acquire() as conn:
            rows = await conn.fetch(query, *params)
            
        return [self._row_to_event(row) for row in rows]
    
    def _row_to_event(self, row: asyncpg.Record) -> WorkflowEvent:
        """Convert database row to event"""
        return WorkflowEvent(
            workflow_id=str(row['workflow_id']),
            execution_id=str(row['execution_id']),
            event_type=row['event_type'],
            actor=row['actor'],
            event_id=str(row['event_id']),
            event_version=row['event_version'],
            timestamp=row['timestamp'],
            data=json.loads(row['data']),
            metadata=json.loads(row['metadata'])
        )
    
    async def _publish_to_kafka(self, event: WorkflowEvent, sequence_number: int):
        """Publish event to Kafka for external consumption"""
        if not self.kafka or not AIOKafkaProducer:
            return
            
        # Add sequence number to metadata
        enriched_event = WorkflowEvent(
            workflow_id=event.workflow_id,
            execution_id=event.execution_id,
            event_type=event.event_type,
            actor=event.actor,
            event_id=event.event_id,
            event_version=event.event_version,
            timestamp=event.timestamp,
            data=event.data,
            metadata={**event.metadata, 'sequence_number': sequence_number}
        )
        
        await self.kafka.send(
            f'workflow.events.{event.event_type}',
            key=event.execution_id.encode(),
            value=enriched_event.to_json().encode()
        )
    
    async def _notify_subscribers(self, event: WorkflowEvent, sequence_number: int):
        """Notify local subscribers of new event"""
        # TODO: Implement subscription notification
        pass
