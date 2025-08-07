"""
SQLAlchemy models for the orchestration service database tables.
These models are used by Alembic for migrations.
"""

from sqlalchemy import Column, String, Integer, DateTime, JSON, BigInteger, Boolean, Text, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import TIMESTAMP
import uuid

Base = declarative_base()

class WorkflowEvent(Base):
    """Event Store table for workflow events"""
    __tablename__ = 'workflow_events'
    
    # Use String for UUIDs to match EventStore usage
    event_id = Column(String(36), primary_key=True)
    workflow_id = Column(String(36), nullable=False, index=True)
    execution_id = Column(String(36), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_version = Column(Integer, default=1)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    actor = Column(String(255), nullable=False)
    data = Column(JSONB, nullable=False)
    event_metadata = Column(JSONB, nullable=False, default={})
    
    # Deterministic ordering
    sequence_number = Column(BigInteger, unique=True, autoincrement=True)
    
    # Timestamp for partitioning later if needed
    created_at = Column(TIMESTAMP(timezone=True), server_default='NOW()', index=True)

class ExecutionSnapshot(Base):
    """Execution state snapshots for fast recovery"""
    __tablename__ = 'execution_snapshots'
    
    snapshot_id = Column(String(36), primary_key=True)
    execution_id = Column(String(36), nullable=False, index=True)
    workflow_id = Column(String(36), nullable=False)
    sequence_number = Column(BigInteger, nullable=False)
    state = Column(JSONB, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default='NOW()')
    
    # Add the unique constraint that's in the migration
    __table_args__ = (
        UniqueConstraint('execution_id', 'sequence_number', name='uq_execution_sequence'),
    )
