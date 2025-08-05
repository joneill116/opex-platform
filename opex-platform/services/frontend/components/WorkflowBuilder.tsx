'use client'

import { useState, useCallback } from 'react'
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  NodeTypes,
  BackgroundVariant,
  Panel,
} from 'reactflow'
import 'reactflow/dist/style.css'

import ComponentPalette from './ComponentPalette'
import WorkflowNode from './WorkflowNode'
import { Workflow, Component, ComponentType } from '@/lib/types/workflow'
import { useUpdateWorkflow } from '@/lib/hooks/useWorkflows'
import { Save, Play, RotateCcw } from 'lucide-react'

interface WorkflowBuilderProps {
  workflow: Workflow
}

const nodeTypes: NodeTypes = {
  workflow: WorkflowNode,
}

export default function WorkflowBuilder({ workflow }: WorkflowBuilderProps) {
  const updateWorkflow = useUpdateWorkflow(workflow.id)
  
  // Convert workflow components to ReactFlow nodes
  const initialNodes: Node[] = workflow.components.map(component => ({
    id: component.id,
    type: 'workflow',
    position: component.position,
    data: {
      label: component.name,
      type: component.type,
      config: component.config,
    },
  }))

  // Convert workflow connections to ReactFlow edges
  const initialEdges: Edge[] = workflow.connections.map((conn, index) => ({
    id: `e${conn.source_id}-${conn.target_id}`,
    source: conn.source_id,
    target: conn.target_id,
    animated: true,
    style: { stroke: '#6366f1', strokeWidth: 2 },
  }))

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge({
      ...params,
      animated: true,
      style: { stroke: '#6366f1', strokeWidth: 2 },
    }, eds)),
    [setEdges]
  )

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()

      const type = event.dataTransfer.getData('application/reactflow');
      const name = event.dataTransfer.getData('componentName')
      
      if (typeof type === 'undefined' || !type) {
        return;
      }

      const reactFlowBounds = event.currentTarget.getBoundingClientRect()
      const position = {
        x: event.clientX - reactFlowBounds.left - 100,
        y: event.clientY - reactFlowBounds.top - 40,
      }

      const newNode: Node = {
        id: `${type}-${Date.now()}`,
        type: 'workflow',
        position,
        data: {
          label: name,
          type: type as ComponentType,
          config: {},
        },
      }

      setNodes((nds) => nds.concat(newNode))
    },
    [setNodes]
  )

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node.id)
  }, [])

  const handleSave = async () => {
    // Convert ReactFlow nodes/edges back to workflow format
    const components: Component[] = nodes.map(node => ({
      id: node.id,
      type: node.data.type,
      name: node.data.label,
      config: node.data.config || {},
      position: node.position,
    }))

    const connections = edges.map(edge => ({
      source_id: edge.source,
      target_id: edge.target,
    }))

    // For now, just show a save message
    // TODO: Update the backend with components and connections
    updateWorkflow.mutate({
      name: workflow.name,
      description: workflow.description,
      severity: workflow.severity,
      solutions: workflow.solutions,
    })
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <ComponentPalette />
      
      <div className="flex-1 relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          className="bg-gray-50"
        >
          <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#e5e7eb" />
          <Controls className="bg-white border-gray-200" />
          
          <Panel position="top-center" className="bg-white px-4 py-2 shadow-lg rounded-lg m-4">
            <h1 className="text-xl font-semibold text-gray-800">{workflow.name}</h1>
          </Panel>
          
          <Panel position="top-right" className="m-4">
            <div className="flex gap-2">
              <button
                onClick={() => window.location.reload()}
                className="p-2 bg-white text-gray-600 rounded-lg shadow hover:shadow-md transition-shadow"
                title="Reset"
              >
                <RotateCcw className="w-5 h-5" />
              </button>
              <button
                className="p-2 bg-green-500 text-white rounded-lg shadow hover:bg-green-600 transition-colors"
                title="Run Workflow"
              >
                <Play className="w-5 h-5" />
              </button>
              <button
                onClick={handleSave}
                disabled={updateWorkflow.isPending}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg shadow hover:bg-blue-600 transition-colors flex items-center gap-2 font-medium"
              >
                <Save className="w-4 h-4" />
                {updateWorkflow.isPending ? 'Saving...' : 'Save'}
              </button>
            </div>
          </Panel>
        </ReactFlow>
      </div>
    </div>
  )
}
