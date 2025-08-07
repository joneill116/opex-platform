"""Initial metadata service setup

Revision ID: 001
Revises: 
Create Date: 2025-08-06 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create workflow_metadata table
    op.create_table('workflow_metadata',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('workflow_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(50), nullable=False, default='1.0.0'),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('schema_version', sa.String(20), nullable=False, default='1.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(36), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('workflow_id', name='uq_workflow_metadata_workflow_id'),
        sa.Index('idx_workflow_metadata_name', 'name'),
        sa.Index('idx_workflow_metadata_created_by', 'created_by')
    )
    
    # Create component_metadata table
    op.create_table('component_metadata',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('component_type', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(50), nullable=False, default='1.0.0'),
        sa.Column('schema', sa.JSON(), nullable=True),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('component_type', 'name', 'version', name='uq_component_metadata_type_name_version'),
        sa.Index('idx_component_metadata_type', 'component_type')
    )


def downgrade() -> None:
    op.drop_table('component_metadata')
    op.drop_table('workflow_metadata')
