from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class WorkflowMetadata(Base):
    __tablename__ = 'workflow_metadata'
    
    id = Column(String(36), primary_key=True)
    workflow_id = Column(String(36), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=False, default='1.0.0')
    tags = Column(JSON, nullable=True)
    schema_version = Column(String(20), nullable=False, default='1.0')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(36), nullable=False)

class ComponentMetadata(Base):
    __tablename__ = 'component_metadata'
    
    id = Column(String(36), primary_key=True)
    component_type = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=False, default='1.0.0')
    schema = Column(JSON, nullable=True)
    configuration = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
