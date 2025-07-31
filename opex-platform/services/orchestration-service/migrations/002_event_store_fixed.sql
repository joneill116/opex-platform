-- Drop tables if they exist (clean slate)
DROP TABLE IF EXISTS workflow_events CASCADE;
DROP TABLE IF EXISTS execution_snapshots CASCADE;

-- Event Store: The source of truth for all workflow execution
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
    
    -- Timestamp for partitioning later if needed
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for fast queries
CREATE INDEX idx_workflow_events_workflow ON workflow_events(workflow_id, sequence_number);
CREATE INDEX idx_workflow_events_execution ON workflow_events(execution_id, sequence_number);
CREATE INDEX idx_workflow_events_type ON workflow_events(event_type, timestamp);
CREATE INDEX idx_workflow_events_created ON workflow_events(created_at);

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

-- Create index for snapshot queries
CREATE INDEX idx_snapshots_execution ON execution_snapshots(execution_id, sequence_number DESC);
