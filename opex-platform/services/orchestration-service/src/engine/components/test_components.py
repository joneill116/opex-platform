import asyncio
import random
from typing import Dict, Any

class BaseComponent:
    """Base class for all components"""
    def __init__(self, component_id: str, config: Dict[str, Any] = None):
        self.component_id = component_id
        self.config = config or {}
    
    async def execute(self, inputs: Dict[str, Any]) -> Any:
        """Execute the component logic"""
        raise NotImplementedError

class DataAcquisitionComponent(BaseComponent):
    """Simulates data acquisition"""
    async def execute(self, inputs: Dict[str, Any]) -> Any:
        print(f"[{self.component_id}] Acquiring data...")
        await asyncio.sleep(1)  # Simulate work
        return {
            "records": [
                {"id": i, "value": random.randint(1, 100)} 
                for i in range(10)
            ],
            "source": self.config.get("source", "test")
        }

class TransformationComponent(BaseComponent):
    """Simulates data transformation"""
    async def execute(self, inputs: Dict[str, Any]) -> Any:
        print(f"[{self.component_id}] Transforming data...")
        await asyncio.sleep(0.5)
        
        # Transform all input records
        all_records = []
        for key, value in inputs.items():
            if isinstance(value, dict) and "records" in value:
                all_records.extend(value["records"])
        
        # Apply transformation
        transformed = [
            {**record, "transformed_value": record["value"] * 2}
            for record in all_records
        ]
        
        return {"records": transformed}

class QualityComponent(BaseComponent):
    """Simulates data quality checks"""
    async def execute(self, inputs: Dict[str, Any]) -> Any:
        print(f"[{self.component_id}] Checking quality...")
        await asyncio.sleep(0.3)
        
        # Check all records
        all_records = []
        for key, value in inputs.items():
            if isinstance(value, dict) and "records" in value:
                all_records.extend(value["records"])
        
        valid_records = [r for r in all_records if r.get("value", 0) > 0]
        
        return {
            "records": valid_records,
            "quality_score": len(valid_records) / len(all_records) if all_records else 0
        }

class PublishComponent(BaseComponent):
    """Simulates publishing results"""
    async def execute(self, inputs: Dict[str, Any]) -> Any:
        print(f"[{self.component_id}] Publishing results...")
        await asyncio.sleep(0.2)
        
        # Count all records
        total_records = 0
        for key, value in inputs.items():
            if isinstance(value, dict) and "records" in value:
                total_records += len(value["records"])
        
        return {
            "status": "published",
            "records_published": total_records,
            "timestamp": "2024-01-01T00:00:00Z"
        }

# Component registry
def create_component_registry():
    """Create a registry of available components"""
    return {
        "source1": DataAcquisitionComponent("source1", {"source": "s3"}),
        "source2": DataAcquisitionComponent("source2", {"source": "api"}),
        "transform": TransformationComponent("transform"),
        "quality": QualityComponent("quality"),
        "publish": PublishComponent("publish")
    }
