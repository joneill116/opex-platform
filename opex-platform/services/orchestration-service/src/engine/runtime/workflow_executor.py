"""
Workflow Executor: Executes workflows exactly as the user designed them.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import uuid
from src.engine.core.event_store import EventStore, WorkflowEvent

class WorkflowExecutor:
    """
    Executes user-defined workflows faithfully.
    No reordering - just smart execution of their design.
    """
    
    def __init__(self, event_store: EventStore, component_registry):
        self.event_store = event_store
        self.components = component_registry
        
    async def execute(self, workflow: Dict, input_data: Optional[Dict] = None) -> str:
        """Execute a workflow exactly as designed by the user"""
        execution_id = str(uuid.uuid4())
        
        # Record start
        await self.event_store.append(WorkflowEvent(
            workflow_id=workflow['id'],
            execution_id=execution_id,
            event_type='workflow.started',
            actor='system',
            data={'input': input_data, 'component_count': len(workflow['components'])}
        ))
        
        # Build execution plan from user's design
        execution_plan = self._build_execution_plan(workflow)
        
        # Execute each layer (respecting user's dependencies)
        results = {}
        for layer in execution_plan:
            # Run components in parallel when user's design allows
            layer_results = await self._execute_layer(
                layer, 
                workflow['id'],
                execution_id,
                results
            )
            results.update(layer_results)
        
        # Record completion
        await self.event_store.append(WorkflowEvent(
            workflow_id=workflow['id'],
            execution_id=execution_id,
            event_type='workflow.completed',
            actor='system',
            data={'outputs': list(results.keys())}
        ))
        
        return execution_id
    
    def _build_execution_plan(self, workflow: Dict) -> List[List[str]]:
        """
        Build execution plan from user's connections.
        Returns layers of components that can run in parallel.
        """
        # Map connections
        dependencies = {}
        for component in workflow['components']:
            dependencies[component['id']] = []
            
        for connection in workflow['connections']:
            target = connection['target']['id']
            source = connection['source']['id']
            dependencies[target].append(source)
        
        # Find execution layers
        layers = []
        executed = set()
        remaining = set(c['id'] for c in workflow['components'])
        
        while remaining:
            # Find components whose dependencies are satisfied
            layer = []
            for comp_id in remaining:
                if all(dep in executed for dep in dependencies[comp_id]):
                    layer.append(comp_id)
            
            if not layer:
                raise ValueError("Circular dependency in workflow!")
                
            layers.append(layer)
            executed.update(layer)
            remaining.difference_update(layer)
            
        return layers
    
    async def _execute_layer(
        self, 
        component_ids: List[str],
        workflow_id: str,
        execution_id: str,
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute components in parallel when possible"""
        tasks = []
        
        for comp_id in component_ids:
            task = self._execute_component(
                comp_id,
                workflow_id,
                execution_id,
                previous_results
            )
            tasks.append(task)
        
        # Run all components in this layer in parallel
        results = await asyncio.gather(*tasks)
        
        # Map results
        return {comp_id: result for comp_id, result in zip(component_ids, results)}
    
    async def _execute_component(
        self,
        component_id: str,
        workflow_id: str,
        execution_id: str,
        previous_results: Dict[str, Any]
    ) -> Any:
        """Execute a single component"""
        # Record start
        await self.event_store.append(WorkflowEvent(
            workflow_id=workflow_id,
            execution_id=execution_id,
            event_type='component.started',
            actor=component_id,
            data={'component_id': component_id}
        ))
        
        try:
            # Get component implementation
            component = self.components.get(component_id)
            
            # Gather inputs from previous results
            inputs = self._gather_inputs(component_id, previous_results)
            
            # Execute component
            result = await component.execute(inputs)
            
            # Record success
            await self.event_store.append(WorkflowEvent(
                workflow_id=workflow_id,
                execution_id=execution_id,
                event_type='component.completed',
                actor=component_id,
                data={'component_id': component_id, 'output_size': len(str(result))}
            ))
            
            return result
            
        except Exception as e:
            # Record failure
            await self.event_store.append(WorkflowEvent(
                workflow_id=workflow_id,
                execution_id=execution_id,
                event_type='component.failed',
                actor=component_id,
                data={'component_id': component_id, 'error': str(e)}
            ))
            raise

    def _gather_inputs(self, component_id: str, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        return previous_results
