from typing import List, Set, Dict, Tuple
import networkx as nx
from dataclasses import dataclass

@dataclass
class ExecutionNode:
    component_id: str
    component_type: str
    estimated_duration: float
    resource_requirements: Dict[str, float]
    
class ExecutionGraph:
    """
    Optimizes workflow execution order for:
    - Maximum parallelism
    - Resource efficiency
    - Minimal latency
    """
    
    def __init__(self, workflow):
        self.workflow = workflow
        self.graph = self._build_graph()
        self._analyze_critical_path()
        
    def _build_graph(self) -> nx.DiGraph:
        """Build directed acyclic graph from workflow"""
        G = nx.DiGraph()
        
        # Add nodes
        for component in self.workflow.components:
            G.add_node(
                component.id,
                data=ExecutionNode(
                    component_id=component.id,
                    component_type=component.type,
                    estimated_duration=self._estimate_duration(component),
                    resource_requirements=self._estimate_resources(component)
                )
            )
        
        # Add edges
        for connection in self.workflow.connections:
            G.add_edge(connection.source_id, connection.target_id)
            
        return G
    
    def get_execution_layers(self) -> List[Set[str]]:
        """
        Returns components grouped by execution layer.
        Components in same layer can run in parallel.
        """
        layers = []
        remaining = set(self.graph.nodes())
        
        while remaining:
            # Find nodes with no dependencies in remaining set
            layer = {
                node for node in remaining
                if all(pred not in remaining for pred in self.graph.predecessors(node))
            }
            
            if not layer:
                raise ValueError("Circular dependency detected!")
                
            layers.append(layer)
            remaining -= layer
            
        return layers
    
    def get_critical_path(self) -> List[str]:
        """Find the longest path - determines minimum execution time"""
        return nx.dag_longest_path(
            self.graph, 
            weight=lambda u, v, d: self.graph.nodes[v]['data'].estimated_duration
        )
    
    def optimize_for_resources(self, available_resources: Dict[str, float]) -> List[List[str]]:
        """
        Optimizes execution order considering resource constraints.
        Returns batches of components to execute together.
        """
        layers = self.get_execution_layers()
        optimized_batches = []
        
        for layer in layers:
            # Bin packing problem - fit components into resource limits
            batches = self._bin_pack_components(layer, available_resources)
            optimized_batches.extend(batches)
            
        return optimized_batches
