CREATE TABLE workflow_events (
    event_id UUID PRIMARY KEY,
    workflow_id UUID NOT NULL,
    execution_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_version INTEGER DEFAULT 1,
    timestamp TIMESTAMPTZ NOT NULL,
    actor VARCHAR(255) NOT NULL,
    data JSONB NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    
    -- Deterministic ordering
    sequence_number BIGSERIAL UNIQUE,
    
    -- Partitioning by workflow for performance
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create indexes for fast queries
CREATE INDEX idx_workflow_events_workflow ON workflow_events(workflow_id, sequence_number);
CREATE INDEX idx_workflow_events_execution ON workflow_events(execution_id, sequence_number);
CREATE INDEX idx_workflow_events_type ON workflow_events(event_type, timestamp);

-- Execution state snapshots for fast recovery
CREATE TABLE execution_snapshots (
    snapshot_id UUID PRIMARY KEY,
    execution_id UUID NOT NULL,
    workflow_id UUID NOT NULL,
    sequence_number BIGINT NOT NULL,
    state JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(execution_id, sequence_number)
);

-- Create first partition
CREATE TABLE workflow_events_2024_01 PARTITION OF workflow_events
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
