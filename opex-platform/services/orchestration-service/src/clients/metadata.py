from opex_common.clients import BaseServiceClient
from typing import List, Optional
from ..config import settings

class MetadataServiceClient(BaseServiceClient):
    def __init__(self):
        super().__init__(settings.METADATA_SERVICE_URL)
    
    async def get_component_templates(self) -> List[dict]:
        return await self.get("/api/v1/component-templates")
    
    async def get_expectation_rules(self, component_type: str) -> List[dict]:
        return await self.get(f"/api/v1/expectation-rules/{component_type}")
